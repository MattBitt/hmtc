from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Tracks"


def TrackRepo():
    return Repository(
        model=TrackModel,
        label="Track",
    )
