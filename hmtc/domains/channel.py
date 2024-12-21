from pathlib import Path
from typing import List
from peewee import ModelSelect
from loguru import logger

from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.repos.channel_repo import ChannelRepo

from hmtc.utils.youtube_functions import download_channel_files

from hmtc.domains.base_domain import BaseDomain

config = init_config()


class Channel(BaseDomain):
    model = ChannelModel
    repo = ChannelRepo()

    def __init__(self, item_id):
        self.instance = self.repo.get_by_id(item_id)
        super().__init__(self.instance)

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
        self.repo.delete_files(self.instance.id)
        self.repo.delete_by_id(item_id=self.instance.id)

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
