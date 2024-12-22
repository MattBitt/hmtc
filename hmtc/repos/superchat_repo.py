from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Superchat as SuperchatModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "Superchats"


def SuperchatRepo():
    return Repository(
        model=SuperchatModel,
        label="Superchat",
    )
