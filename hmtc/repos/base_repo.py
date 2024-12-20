from loguru import logger
from pathlib import Path
from hmtc.config import init_config
from hmtc.decorators import myhandler
from hmtc.models import BaseModel
from hmtc.utils.file_manager import FileManager

config = init_config()


class Repository:
    def __init__(
        self,
        model: BaseModel,
        file_model: BaseModel = None,
        label: str = "",
        filetypes: list[str] = None,
        path: Path = None,
    ):
        self.model = model
        self.label = label
        if file_model is not None:
            self.file_manager = FileManager(
                model=file_model, filetypes=filetypes, path=path
            )

    def get_by_id(self, item_id: int) -> BaseModel:
        return self.model.get_by_id(item_id)

    def create_item(self, data) -> BaseModel:
        return self.model.create(**data)

    def load_or_create_item(self, data) -> BaseModel:
        item, created = self.model.get_or_create(**data)
        return item, created

    def update_item(self, data) -> BaseModel:
        _id = data.pop("id")
        item = self.model.get_by_id(_id)

        for key, value in data.items():
            setattr(item, key, value)

        item.save()
        return item

    def delete_by_id(self, item_id: int) -> None:
        logger.debug(f"Deleting {self.label}: {item_id}")
        self.model.delete_by_id(item_id)
        logger.success(f"Deleted {self.label} {item_id} successfully")

    def count(self):
        return self.model.select().count()

    def get_by(self, **kwargs) -> BaseModel | None:
        return self.model.get_or_none(**kwargs)

    def all(self):
        for item in self.model.select():
            yield item

    def delete_files(self, item_id):
        logger.debug(f"Deleting files for {self.label} {item_id}")
        self.file_manager.delete_files(item_id)
