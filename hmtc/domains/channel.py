from pathlib import Path
from typing import List
from peewee import ModelSelect
from loguru import logger

from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFile as ChannelFileModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository
from hmtc.utils.file_manager import FileManager
from hmtc.utils.youtube_functions import download_channel_files
from hmtc.domains.base_domain import Domain
from hmtc.domains import *

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel(Domain):
    def __init__(self, item_id=None) -> "Channel":
        super().__init__(
            model=ChannelModel,
            label="Channels",
            filetypes=["poster", "thumbnail", "info"],
            item_id=item_id,
        )

    @staticmethod
    def create(data) -> "Channel":
        repo = Repository(ChannelModel, "Channels")
        try:
            channel = repo.create_item(data=data)
        except Exception as e:
            logger.error(f"Error creating channel {data['title']}: {e}")
            raise e
        return Channel(channel.id)

    def update(self, data) -> "Channel":
        new_dict = {"id": self.instance.id, **data}
        self.repo.update_item(data=new_dict)
        return Channel(self.instance.id)

    def delete_me(self) -> None:
        vids = VideoModel.select().where(VideoModel.channel_id == self.instance.id)
        for vid in vids:
            Video.delete_id(vid.id)
        self.repo.delete_by_id(item_id=self.instance.id)

    @property
    def poster(self) -> Path:
        return self.file_manager.get_file(self.instance.id, "poster").name

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.file_manager.add_file(self.instance, file)

    @staticmethod
    def count() -> int:
        return ChannelModel.select().count()

    @staticmethod
    def all() -> ModelSelect:
        return ChannelModel.select()

    @staticmethod
    def get_by(**kwargs) -> "Channel":
        repo = Repository(ChannelModel, "Channels")
        return Channel(repo.get_by(**kwargs).id)

    @staticmethod
    def select_where(**kwargs) -> ModelSelect:
        return ChannelModel.select().where(**kwargs)
