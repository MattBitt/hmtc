from pathlib import Path
from hmtc.domains.series import Series
from hmtc.repos.base_repo import Repository
from hmtc.models import Series as SeriesModel, SeriesFile as SeriesFileModel
from hmtc.config import init_config

config = init_config()
STORAGE = Path(config["STORAGE"]) / "series"


def SeriesRepo():
    return Repository(
        model=SeriesModel,
        label="Series",
        file_model=SeriesFileModel,
        filetypes=["poster", "thumbnail", "info"],
        path=STORAGE,
    )
