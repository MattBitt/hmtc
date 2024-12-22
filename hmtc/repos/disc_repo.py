from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Disc as DiscModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Discs"


def DiscRepo():
    return Repository(
        model=DiscModel,
        label="Disc",
    )
