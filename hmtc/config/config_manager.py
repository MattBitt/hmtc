import os
from pathlib import Path

import tomllib

CONFIG = os.environ.get("HMTC_CONFIG_PATH", None)
assert CONFIG is not None, "HMTC_CONFIG_PATH not set"


class ConfigManager:
    @classmethod
    def from_toml(cls, env: str, config_path: Path):
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            assert "app" in data, "app section missing from config"
            return data


def get_env():
    if "HMTC_ENV" not in os.environ:
        raise ValueError("No HMTC_ENV variable set. Check the .env file")
    return os.environ.get("HMTC_ENV", None)


def get_config_file(file: str):
    config = Path(CONFIG) / file
    if not config.exists():
        raise FileNotFoundError(f"Config file {config} does not exist")
    return config


def init_config():
    env = get_env()
    if env in ["development", "testing", "staging"]:
        file = f"config-{env}.toml"
    else:
        file = "config.toml"
    config = get_config_file(file)
    return ConfigManager.from_toml(env=env, config_path=config)
