from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AppConfig(BaseModel):
    """Application configurations."""

    csv_to_import: str = "config/HarryMackClips.csv"
    import_during_testing: bool = True
    download_during_testing: bool = True
    create_tracks_during_testing: bool = True

    # this file should contain the data to keep checking for new videos
    video_collections_input_file = "config/video_collections.yaml"
    video_collection_error_videos = "config/video_collections_errors.yaml"

    # files should be removed from this file and added to the file below
    # once they have been imported.  no reason to check them over and over again
    individual_videos_input_file = "config/individual_videos.yaml"
    individual_videos_output_file = "config/individual_videos_imported.yaml"


class GlobalConfig(BaseSettings):
    """Global configurations."""

    # These variables will be loaded from the .env file. However, if
    # there is a shell environment variable having the same name,
    # that will take precedence.

    APP_CONFIG: AppConfig = AppConfig()

    # define global variables with the Field class
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    LOG_LEVEL: str = Field("ERROR", env="LOG_LEVEL")
    APP_VER: str = Field("Not Found", env="APP_VER")
    # environment specific variables do not need the Field class

    PLEXURL = "http://192.168.0.202:32400"
    TAUTULLI_URL = "http://192.168.0.202:8181"
    SERVER_HOST: Optional[str] = None
    SERVER_PORT: Optional[str] = None
    DOWNLOAD_PATH: Optional[str] = None
    SOURCE_ROOT_PATH: Optional[str] = None
    TRACK_ROOT_PATH: Optional[str] = None

    class Config:
        """Loads the dotenv file."""

        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""

    class Config:
        env_prefix: str = "DEV_"


class TestConfig(GlobalConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "TEST_"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "PROD_"


class FactoryConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        elif self.env_state == "prod":
            return ProdConfig()

        elif self.env_state == "test":
            return TestConfig()


cnf = FactoryConfig(GlobalConfig().ENV_STATE)()
