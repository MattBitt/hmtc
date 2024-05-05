from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["hmtc/settings.toml", "hmtc/.secrets.toml"],
)
