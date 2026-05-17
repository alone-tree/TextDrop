from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .constants import CONFIG_DIR_NAME, CONFIG_FILE_NAME
from .tokens import generate_token


@dataclass
class AppConfig:
    token: str
    language: str = "zh"
    selected_address: str | None = None


def config_path() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".config"
    return base / CONFIG_DIR_NAME / CONFIG_FILE_NAME


def load_config() -> AppConfig:
    path = config_path()
    if not path.exists():
        config = AppConfig(token=generate_token())
        save_config(config)
        return config

    data = json.loads(path.read_text(encoding="utf-8"))
    token = data.get("token") or generate_token()
    language = data.get("language") if data.get("language") in {"zh", "en"} else "zh"
    selected_address = data.get("selected_address")
    return AppConfig(token=token, language=language, selected_address=selected_address)


def save_config(config: AppConfig) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

