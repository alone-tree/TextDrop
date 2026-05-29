# Copyright (C) 2026  alone-tree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations

import ipaddress
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from .config import config_dir_path


CERTIFICATE_DAYS = 825
RENEW_BEFORE_DAYS = 30
TLS_CERT_FILE_NAME = "local_https_cert.pem"
TLS_KEY_FILE_NAME = "local_https_key.pem"
TLS_META_FILE_NAME = "local_https_meta.json"


@dataclass(frozen=True)
class TlsPaths:
    certfile: Path
    keyfile: Path


def ensure_tls_certificate(hosts: Iterable[str]) -> tuple[TlsPaths, bool]:
    config_dir = config_dir_path()
    config_dir.mkdir(parents=True, exist_ok=True)
    certfile = config_dir / TLS_CERT_FILE_NAME
    keyfile = config_dir / TLS_KEY_FILE_NAME
    metafile = config_dir / TLS_META_FILE_NAME
    normalized_hosts = _normalize_hosts(hosts)

    paths = TlsPaths(certfile=certfile, keyfile=keyfile)
    if _certificate_is_current(certfile, keyfile, metafile, normalized_hosts):
        return paths, False

    _write_certificate(certfile, keyfile, metafile, normalized_hosts)
    return paths, True


def _normalize_hosts(hosts: Iterable[str]) -> list[str]:
    values = {"localhost", "127.0.0.1"}
    for host in hosts:
        value = str(host).strip()
        if value:
            values.add(value)
    return sorted(values)


def _certificate_is_current(certfile: Path, keyfile: Path, metafile: Path, hosts: list[str]) -> bool:
    if not certfile.exists() or not keyfile.exists() or not metafile.exists():
        return False
    try:
        metadata = json.loads(metafile.read_text(encoding="utf-8"))
        expires_at = datetime.fromisoformat(metadata.get("expires_at", ""))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False
    if metadata.get("hosts") != hosts:
        return False
    return expires_at > datetime.now(timezone.utc) + timedelta(days=RENEW_BEFORE_DAYS)


def _write_certificate(certfile: Path, keyfile: Path, metafile: Path, hosts: list[str]) -> None:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=CERTIFICATE_DAYS)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "TextDrop"),
            x509.NameAttribute(NameOID.COMMON_NAME, "TextDrop Local HTTPS"),
        ]
    )
    san_values = [_subject_alt_name(host) for host in hosts]
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(expires_at)
        .add_extension(x509.SubjectAlternativeName(san_values), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(private_key, hashes.SHA256())
    )

    keyfile.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    certfile.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    metafile.write_text(
        json.dumps({"hosts": hosts, "expires_at": expires_at.isoformat()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _subject_alt_name(host: str) -> x509.GeneralName:
    try:
        return x509.IPAddress(ipaddress.ip_address(host))
    except ValueError:
        return x509.DNSName(host)
