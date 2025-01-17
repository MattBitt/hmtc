from pathlib import Path
from typing import List

from loguru import logger
from peewee import ModelSelect
from PIL import Image

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFiles
from hmtc.repos.channel_repo import ChannelRepo
from hmtc.repos.file_repo import FileRepo
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel(BaseDomain):
    model = ChannelModel
    repo = ChannelRepo()
    file_repo = FileRepo(ChannelFiles)

    def serialize(self):
        file_dict = {}
        # for file in self.fm.files(self.instance.id):
        #     file_dict[file.filetype] = file.name

        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "youtube_id": self.instance.youtube_id,
            "url": self.instance.url,
            # "files": self.fm.files(self.instance.id),
            "auto_update": self.instance.auto_update,
            "last_update_completed": self.instance.last_update_completed,
            "files": file_dict,
        }

    @classmethod
    def last_update_completed_at(cls):
        return (
            cls.repo.model.select()
            .order_by(cls.repo.model.last_update_completed.desc())
            .first()
            .last_update_completed
        )

    # the methods for the domains that include files
    def add_file(self, file: Path):

        target_path = STORAGE / self.instance.youtube_id
        new_name = self.instance.youtube_id

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    @classmethod
    def to_auto_update(cls):
        channels = ChannelModel.select().where(
            ChannelModel.title.contains("Harry Mack")
        )
        return [c.url for c in channels]
