from pathlib import Path
from typing import Any, Optional, Generator

from loguru import logger

from hmtc.config import init_config
from hmtc.models import BaseModel

config = init_config()


class Repository:
    def __init__(self, model: BaseModel, label: str = ""):
        self.model = model
        self.label = label

    def get_by_id(self, item_id: int) -> BaseModel:
        return self.model.get_by_id(item_id)

    def create_item(self, data: dict) -> BaseModel:
        return self.model.create(**data)

    def load_or_create_item(self, data: dict) -> tuple[BaseModel, bool]:
        item, created = self.model.get_or_create(**data)
        return item, created

    def update_item(self, data: dict) -> BaseModel:
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

    def count(self) -> int:
        return self.model.select().count()

    def get_by(self, **kwargs: Any) -> Optional[BaseModel]:
        return self.model.get_or_none(**kwargs)

    def all(self) -> Generator[BaseModel, None, None]:
        for item in self.model.select():
            yield item
