from pathlib import Path
from typing import List

from loguru import logger
from peewee import ModelSelect

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Channel as ChannelModel
from hmtc.repos.channel_repo import ChannelRepo
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = Path(config["STORAGE"]) / "channels"


class Channel(BaseDomain):
    model = ChannelModel
    repo = ChannelRepo()
    # fm = FileManager(
    #     model=ChannelFileModel, filetypes=["poster", "thumbnail", "info"], path=STORAGE
    # )

    def delete_me(self) -> None:
        self.fm.delete_files(self.instance.id)
        self.repo.delete_by_id(item_id=self.instance.id)

    def download_files(self):
        files = download_channel_files(self.instance.youtube_id, self.instance.url)
        for file in files:
            self.fm.add_file(self, file)

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
