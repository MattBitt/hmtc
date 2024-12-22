from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Albums"


def AlbumRepo():
    return Repository(
        model=AlbumModel,
        label="Album",
    )
