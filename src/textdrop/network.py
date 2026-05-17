from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass

import psutil


EXCLUDED_INTERFACE_KEYWORDS = (
    "bluetooth",
    "container",
    "docker",
    "hyper-v",
    "isatap",
    "loopback",
    "npcap",
    "tap",
    "teredo",
    "tun",
    "vbox",
    "vethernet",
    "virtual",
    "vmware",
    "vpn",
    "wintun",
    "wireguard",
    "zerotier",
)

PREFERRED_INTERFACE_KEYWORDS = (
    "ethernet",
    "wi-fi",
    "wifi",
    "wireless",
    "wlan",
    "以太网",
    "无线",
)


@dataclass(frozen=True)
class AddressCandidate:
    address: str
    interface: str
    score: int

    @property
    def label(self) -> str:
        return f"{self.interface} - {self.address}"


def find_available_port(start_port: int) -> int:
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", port))
            except OSError:
                port += 1
                continue
            return port
    raise RuntimeError("No available port found.")


def list_address_candidates() -> list[AddressCandidate]:
    stats = psutil.net_if_stats()
    candidates: list[AddressCandidate] = []
    seen: set[str] = set()

    for interface, addrs in psutil.net_if_addrs().items():
        if interface in stats and not stats[interface].isup:
            continue
        for addr in addrs:
            if addr.family != socket.AF_INET:
                continue
            ip = addr.address
            if ip in seen or not _is_usable_ipv4(ip):
                continue
            seen.add(ip)
            candidates.append(AddressCandidate(ip, interface, _score_interface(interface, ip)))

    if not candidates:
        fallback = _route_address()
        if fallback:
            candidates.append(AddressCandidate(fallback, "Default", 0))

    return sorted(candidates, key=lambda item: (-item.score, item.interface.lower(), item.address))


def choose_address(candidates: list[AddressCandidate], saved_address: str | None) -> str:
    addresses = {candidate.address for candidate in candidates}
    if saved_address in addresses:
        return saved_address
    if candidates:
        return candidates[0].address
    return "127.0.0.1"


def _is_usable_ipv4(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    return not (
        ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or value.startswith("169.254.")
    )


def _score_interface(interface: str, address: str) -> int:
    name = interface.lower()
    ip = ipaddress.ip_address(address)
    score = 0
    if ip.is_private:
        score += 100
    if any(keyword in name for keyword in PREFERRED_INTERFACE_KEYWORDS):
        score += 50
    if any(keyword in name for keyword in EXCLUDED_INTERFACE_KEYWORDS):
        score -= 100
    return score


def _route_address() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            address = sock.getsockname()[0]
            return address if _is_usable_ipv4(address) else None
    except OSError:
        return None

