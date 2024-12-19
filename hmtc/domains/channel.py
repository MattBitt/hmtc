from pathlib import Path
from typing import List

from loguru import logger

from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFile as ChannelFileModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository
from hmtc.utils.file_manager import FileManager
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel:
    model = ChannelModel()
    repo = Repository(model=model, label="Channel")
    filetypes = ["poster", "thumbnail", "info"]
    file_manager = FileManager(
        model=ChannelFileModel, filetypes=filetypes, path=STORAGE
    )

    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.instance = self.load(channel_id)

    @classmethod
    def create(cls, data) -> ChannelModel:
        _channel = (
            ChannelModel.select()
            .where(ChannelModel.youtube_id == data["youtube_id"])
            .get_or_none()
        )
        if _channel is not None:
            return _channel

        try:
            channel = cls.repo.create_item(data=data)
        except Exception as e:
            logger.error(f"Error creating channel {data['title']}: {e}")

        return channel

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.add_file(self.instance, file)

    @classmethod
    def get_by(cls, **kwargs) -> "Channel":
        return cls(cls.repo.get_by(**kwargs))

    @classmethod
    def load(cls, item_id) -> ChannelModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> ChannelModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[ChannelModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        return item.my_dict()

    @classmethod
    def delete_id(cls, item_id) -> None:
        # importing here to avoid circular import
        # probably not the best way to do it
        from hmtc.domains.video import Video

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

    def add_file(self, file: Path) -> None:
        self.file_manager.add_file(self.instance, file)

    @property
    def poster(self) -> Path:
        return self.file_manager.get_file(self.instance.id, "poster").name
