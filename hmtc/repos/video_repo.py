from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Videos"


def VideoRepo():
    return Repository(
        model=VideoModel,
        label="Video",
    )
