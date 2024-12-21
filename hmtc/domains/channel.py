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

from hmtc.domains import *

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel:
    model = ChannelModel
    file_model = ChannelFileModel
    repo = Repository(
        model,
        file_model,
        "Channels",
        filetypes=["poster", "thumbnail", "info"],
        path=STORAGE,
    )

    def __init__(self, item_id=None):
        if item_id:
            self.instance = self.repo.get_by_id(item_id=item_id)
        else:
            logger.debug("Creating new Channel instance")
            self.instance = ChannelModel()

    @classmethod
    def create(cls, data) -> "Channel":
        channel = cls.repo.create_item(data=data)
        return Channel.get_by(id=channel.id)

    @classmethod
    def get_by(cls, **kwargs) -> "Channel":
        return Channel(cls.repo.get_by(**kwargs).id)

    @classmethod
    def select_where(cls, **kwargs) -> ModelSelect:
        return cls.model.query_from_kwargs(**kwargs)

    @classmethod
    def order_by(cls, **kwargs) -> ModelSelect:
        return cls.model.order_by_kwargs(**kwargs)

    @classmethod
    def count(cls) -> int:
        return cls.repo.count()

    @classmethod
    def all(cls) -> ModelSelect:
        return cls.repo.all()

    def update(self, data) -> "Channel":
        new_dict = {"id": self.instance.id, **data}
        self.repo.update_item(data=new_dict)
        return Channel(self.instance.id)

    def delete_me(self) -> None:
        vids = VideoModel.select().where(VideoModel.channel_id == self.instance.id)
        for vid in vids:
            pass
            # Video.delete_id(vid.id)

        self.repo.delete_files(self.instance.id)
        self.repo.delete_by_id(item_id=self.instance.id)

    def serialize(self) -> dict:
        return self.instance.my_dict()

    def file_count(self) -> dict:
        return self.repo.file_manager.count_all()

    @property
    def poster(self) -> Path:
        return self.repo.file_manager.get_file(self.instance.id, "poster").name

    def add_file(self, file: Path):
        self.repo.file_manager.add_file(self.instance, file)

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.repo.file_manager.add_file(self.instance, file)
