from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Sections"


def SectionRepo():
    return Repository(
        model=SectionModel,
        label="Section",
    )
