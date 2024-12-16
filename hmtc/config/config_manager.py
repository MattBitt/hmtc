import os
from pathlib import Path

import tomllib


class ConfigManager:

    @classmethod
    def from_toml(cls, config_path: Path):
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            if Path("/app/config").exists():
                # this is running in docker
                # should only be staging/production
                if "paths" in data:
                    raise ValueError(
                        "paths section should not be in config while running in docker"
                    )

                data["WORKING"] = Path("/app/working")
                data["STORAGE"] = Path("/app/storage")
            else:
                data["WORKING"] = Path(data["paths"]["working"])
                data["STORAGE"] = Path(data["paths"]["storage"])

            assert "app" in data, "app section missing from config"
            return data

    @property
    def WORKING(self):
        return Path(self["paths"]["working"])

    @property
    def STORAGE(self):
        return Path(self["paths"]["storage"])


def get_env():
    if "HMTC_ENV" not in os.environ:
        raise ValueError("No HMTC_ENV variable set. Check the .env file")
    return os.environ.get("HMTC_ENV", None)


def get_config_file(file: str):
    if Path("/app/config").exists():
        CONFIG = "/app/config"
    else:
        CONFIG = "hmtc/config"

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
    return ConfigManager.from_toml(config_path=config)
