import os
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    baseDir: str = "D:/weatherData"
    thread_pool_size: int = 4
    port: int = 8000


_settings: Settings = None


def load_config(config_path: str = None) -> Settings:
    global _settings
    if config_path is None:
        config_path = os.environ.get(
            "CONFIG_PATH",
            None
        )
        if config_path is None:
            # Fallback: use exe directory in frozen mode, else default path
            if getattr(sys, 'frozen', False):
                config_path = os.path.join(os.path.dirname(sys.executable), 'config.yaml')
            else:
                config_path = Path(__file__).parent.parent.parent / "config.yaml"

    # Ensure config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    _settings = Settings(**config_data)
    return _settings


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_config()
    return _settings
