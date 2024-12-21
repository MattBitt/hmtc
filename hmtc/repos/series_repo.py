from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Series as SeriesModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "series"


def SeriesRepo():
    return Repository(
        model=SeriesModel,
        label="Series",
    )
