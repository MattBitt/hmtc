from typing import List, Protocol
from pathlib import Path
from peewee import ModelSelect
from hmtc.utils.file_manager import FileManager
from hmtc.repos.base_repo import Repository
from hmtc.config import init_config

config = init_config()
STORAGE = Path(config["STORAGE"])


class Domain(Protocol):
    def __init__(
        self,
        model: type,
        repo: Repository,
        filetypes: List[str],
        file_manager: FileManager,
        instance: type,
    ):
        self.model = model
        self.repo = repo
        self.filetypes = filetypes
        self.file_manager = file_manager
        self.instance = instance

    def create(self, data) -> "Domain": ...

    def get_by(self, **kwargs) -> ModelSelect | None: ...

    def download_files(self) -> List[Path] | None: ...

    def delete_me(self) -> None: ...

    def update(self, data) -> "Domain": ...

    def all(self) -> List[ModelSelect]: ...
