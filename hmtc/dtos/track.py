from pathlib import Path
from dataclasses import dataclass
from hmtc.models import Track
from hmtc.config import init_config
from loguru import logger

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"])


class BaseDTO:
    pass


@dataclass(frozen=True, kw_only=True)
class TrackDTO(BaseDTO):
    title: str = True
    track_number: str = True
    # album: ForeignKeyField , backref="tracks", null=True
    # video: ForeignKeyField , backref="tracks", null=True
    start_time: int = True
    length: int = True
    end_time: int = True
    words: str = True
    notes: str = True
    jf_id: str = True
