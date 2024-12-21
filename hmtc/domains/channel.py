from pathlib import Path
from typing import List

from loguru import logger
from peewee import ModelSelect

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFile as ChannelFileModel
from hmtc.repos.channel_repo import ChannelRepo
from hmtc.utils.file_manager import FileManager
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel(BaseDomain):
    model = ChannelModel
    repo = ChannelRepo()
    fm = FileManager(
        model=ChannelFileModel, filetypes=["poster", "thumbnail", "info"], path=STORAGE
    )

    def delete_me(self) -> None:
        self.fm.delete_files(self.instance.id)
        self.repo.delete_by_id(item_id=self.instance.id)

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.fm.add_file(self.instance, file)
