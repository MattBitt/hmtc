from pathlib import Path
from typing import List
from peewee import ModelSelect
from loguru import logger

from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.utils.youtube_functions import download_channel_files
from hmtc.domains.base_domain import Domain

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
