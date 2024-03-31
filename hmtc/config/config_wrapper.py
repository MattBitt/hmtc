import configparser
import os


class ConfigWrapper:
    def create_instance(self) -> configparser.ConfigParser:
        env = os.environ.get("ENVIRONMENT", None)
        if env is None:
            print(
                "The envrionment variable: 'ENVIRONMENT' was not set. Defaulting to 'dev'"
            )
            env = "dev"
            os.environ["ENVIRONMENT"] = env

        config_parser = configparser.ConfigParser(
            os.environ, interpolation=configparser.ExtendedInterpolation()
        )
        dir_name = os.path.dirname(__file__)

        base_ini_file = os.path.join(dir_name, "settings.ini")
        if not os.path.exists(base_ini_file):
            print(
                f"ERROR: The base INI file {base_ini_file} was not found in this directory"
            )
            exit()

        environment_specific_ini_file = os.path.join(dir_name, f"settings.{env}.ini")
        if not os.path.exists(environment_specific_ini_file):
            print(
                f"The environment specific INI file '{environment_specific_ini_file}' was not found in this directory"
            )
            exit()

        config_parser.read(base_ini_file)
        config_parser.read(environment_specific_ini_file)
        return config_parser


def init_config():
    return ConfigWrapper().create_instance()
