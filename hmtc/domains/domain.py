from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from peewee import ModelSelect
from hmtc.utils.file_manager import FileManager
from hmtc.repos.base_repo import Repository
from hmtc.config import init_config

config = init_config()
STORAGE = Path(config["STORAGE"])


class Domain(ABC):

    def __init__(self, model, label, filetypes, item_id=None):
        self.model = model
        self.repo = Repository(model, label)
        self.filetypes = ["poster", "thumbnail", "info"]
        self.file_manager = FileManager(model=model, filetypes=filetypes, path=STORAGE)
        if item_id:
            self.instance = self.repo.load_item(item_id=item_id)
        else:
            self.instance = model()

    @abstractmethod
    def create(self, data) -> "Domain":
        pass

    @abstractmethod
    def get_by(self, **kwargs) -> ModelSelect | None:
        pass

    @abstractmethod
    def download_files(self) -> List[Path] | None:
        pass

    @abstractmethod
    def delete_me(self) -> None:
        pass

    @abstractmethod
    def update(self) -> "Domain":
        pass

    @abstractmethod
    def all(self) -> List[ModelSelect]:
        pass
