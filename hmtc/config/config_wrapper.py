import configparser
import os
from enum import Enum
from pathlib import Path


class env(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

    def __str__(self):
        return self.value

    @staticmethod
    def from_string(s):
        try:
            return env[s]
        except KeyError:
            raise ValueError()

    @staticmethod
    def from_string_ignore_case(s):
        try:
            return env[s.upper()]
        except KeyError:
            raise ValueError()

    @staticmethod
    def config_file_name(s):
        return f"settings.{s}.ini"


class ConfigWrapper:
    @classmethod
    def create_instance(self) -> configparser.ConfigParser:
        current_env = os.environ.get("ENVIRONMENT", env.DEVELOPMENT)
        # if current_env is None:
        #     print(
        #         "The envrionment variable: 'ENVIRONMENT' was not set. Defaulting to 'dev'"
        #     )
        #     current_env = "development"
        #     os.environ["ENVIRONMENT"] = current_env

        config_parser = configparser.ConfigParser(
            os.environ, interpolation=configparser.ExtendedInterpolation()
        )
        # need a better way to do this for launch .json
        # works fine for docker/docker-compose

        config_dir = Path("/config/")
        if config_dir.exists():
            dir_name = config_dir
        else:
            print(
                "The /config/ directory was not found. Checking the current directory"
            )
            dir_name = Path("./hmtc/config")
        base_ini_file = os.path.join(dir_name, "settings.base.ini")
        if not os.path.exists(base_ini_file):
            print(
                f"ERROR: The base INI file {base_ini_file} was not found in this directory"
            )
            exit()

        environment_specific_ini_file = os.path.join(
            dir_name, f"settings.{current_env}.ini"
        )
        if not os.path.exists(environment_specific_ini_file):
            print(
                f"The environment specific INI file '{environment_specific_ini_file}' was not found in this directory"
            )
            exit()

        config_parser.read(base_ini_file)
        config_parser.read(environment_specific_ini_file)
        return config_parser


def init_config():
    return ConfigWrapper.create_instance()
