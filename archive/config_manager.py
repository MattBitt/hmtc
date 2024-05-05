from pydantic import BaseSettings


class ConfigManager(BaseSettings):

    app_name: str = "Harry Mack Track Creator"
    debug: bool
    db_name: str = "hmtc-"
    db_host: str
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"

    class Config:
        env_file = ".env"
        env_prefix = "HMTC_"

        @classmethod
        def from_env(cls, env: str):
            env_file = f".env.{env}"
            return cls(_env_file=env_file)


# Load settings for the 'production' environment
# settings = Settings.from_env('production')
