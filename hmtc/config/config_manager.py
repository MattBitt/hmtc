import os
import tomllib
from pathlib import Path

from loguru import logger

# from dotenv import load_dotenv

# load_dotenv()  # take environment variables from .env


# env folders
#
# [PATHS]
# DOWNLOAD=${WORKING}/downloads
# UPLOAD=${WORKING}/uploads
# TEMP=${WORKING}/temp

# MEDIA=${STORAGE}/media


# class env(Enum):
#     DEVELOPMENT = "development"
#     PRODUCTION = "production"
#     TESTING = "testing"
#     STAGING = "staging"

#     def __str__(self):
#         return self.value

#     @staticmethod
#     def from_string(s):
#         try:
#             return env[s]
#         except KeyError:
#             raise ValueError()

#     @staticmethod
#     def from_string_ignore_case(s):
#         try:
#             return env[s.upper()]
#         except KeyError:
#             raise ValueError()

#     @staticmethod
#     def config_filename(s):
#         return f"settings.{s}.ini"


class ConfigManager:
    @classmethod
    def from_toml(cls, env: str, config_path: Path):
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return data


def get_env():
    e = os.environ.get("HMTC_ENV", None)
    if "HMTC_ENV" not in os.environ:
        raise ValueError("No HMTC_ENV variable set. Check the .env file")
    return e


def get_config_file(file: str):
    config = Path(os.environ.get("HMTC_CONFIG_PATH")) / file
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
