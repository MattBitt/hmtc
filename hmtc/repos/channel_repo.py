from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFile as ChannelFileModel
from hmtc.repos.base_repo import Repository

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


def ChannelRepo():
    return Repository(
        model=ChannelModel,
        label="Channel",
    )
