from pathlib import Path

from hmtc.config import init_config
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "SuperchatSegments"


def SuperchatSegmentRepo():
    return Repository(
        model=SuperchatSegmentModel,
        label="SuperchatSegment",
    )
