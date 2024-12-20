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
from hmtc.domains.domain import Domain
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

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.file_manager.add_file(self.instance, file)

    @classmethod
    def create(self, data) -> "Channel":
        try:
            channel = self.repo.create_item(data=data)
        except Exception as e:
            logger.error(f"Error creating channel {data['title']}: {e}")

        return Channel(channel.id)

    def delete_me(self):
        self.delete_id(self.instance.id)

    @classmethod
    def get_by(cls, **kwargs) -> "Channel":
        return cls(cls.repo.get_by(**kwargs))

    @classmethod
    def update(cls, data) -> ChannelModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[ModelSelect]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        return item.my_dict()

    @classmethod
    def delete_id(cls, item_id) -> None:
        vids = VideoModel.select().where(VideoModel.channel_id == item_id)
        for vid in vids:
            Video.delete_id(vid.id)
        cls.repo.delete_by_id(item_id=item_id)

    @staticmethod
    def last_update_completed() -> str | None:
        channel = (
            ChannelModel.select(ChannelModel.last_update_completed)
            .where(ChannelModel.auto_update == True)
            .order_by(ChannelModel.last_update_completed.desc())
            .limit(1)
            .get_or_none()
        )

        if channel:
            return str(channel.last_update_completed)

        return None

    @classmethod
    def to_auto_update(cls):
        channels = ChannelModel.select().where(ChannelModel.auto_update == True)
        for channel in channels:
            yield channel
        else:
            return None

    @classmethod
    def count(cls):
        return ChannelModel.select().count()

    @property
    def poster(self) -> Path:
        return self.file_manager.get_file(self.instance.id, "poster").name

    def all(self):
        pass
