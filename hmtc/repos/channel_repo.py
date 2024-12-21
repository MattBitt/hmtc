from pathlib import Path
from hmtc.repos.base_repo import Repository
from hmtc.models import Channel as ChannelModel, ChannelFile as ChannelFileModel
from hmtc.config import init_config

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


def ChannelRepo():
    return Repository(
        model=ChannelModel,
        label="Channel",
        file_model=ChannelFileModel,
        filetypes=["poster", "thumbnail", "info"],
        path=STORAGE,
    )
