import os
import tomllib
from pathlib import Path

from loguru import logger

CONFIG = os.environ.get("HMTC_CONFIG_PATH", "/workspace/working")
assert CONFIG is not None, "HMTC_CONFIG_PATH not set"


class ConfigManager:
    @classmethod
    def from_toml(cls, env: str, config_path: Path):
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            assert "app" in data, "app section missing from config"
            return data


def get_env():
    e = os.environ.get("HMTC_ENV", None)
    if "HMTC_ENV" not in os.environ:
        raise ValueError("No HMTC_ENV variable set. Check the .env file")
    return e


def get_config_file(file: str):

    config = Path(CONFIG) / file
    if not config.exists():

        raise FileNotFoundError(f"Config file {config} does not exist")
    return config


def check_paths():
    storage = "get this from the config file"
    working = "get this from the config file"

    paths = [
        {"name": "storage", "path_type": storage},
        {"name": "working", "path_type": working},
    ]

    for p in paths:
        if p["path_type"] is None:
            raise ValueError(f"{p['name']} is not set. Check the .env file")
        if not Path(p).exists():
            raise FileNotFoundError(f"Path {p['name']} does not exist")
    return paths


def init_config():

    try:
        env = get_env()
        if env in ["development", "testing", "staging"]:
            file = f"config-{env}.toml"
        else:
            file = "config.toml"
        config = get_config_file(file)
        logger.debug(f"Loading {env} config from {config}")
        return ConfigManager.from_toml(env=env, config_path=config)
    except:
        raise
