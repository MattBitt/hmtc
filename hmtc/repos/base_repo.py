from loguru import logger

from hmtc.config import init_config
from hmtc.decorators import myhandler
from hmtc.models import BaseModel

config = init_config()


class Repository:
    def __init__(self, model: BaseModel, label: str):
        self.model = model
        self.label = label

    @myhandler
    def load_item(self, item_id: int) -> BaseModel:
        return self.model.get_by_id(item_id)

    @myhandler
    def create_item(self, data) -> BaseModel:
        return self.model.create(**data)

    @myhandler
    def load_or_create_item(self, data) -> BaseModel:
        item = self.model.get_or_create(**data)
        return item

    @myhandler
    def update_item(self, data) -> BaseModel:
        _id = data.pop("id")
        item = self.model.get_by_id(_id)

        for key, value in data.items():
            setattr(item, key, value)

        item.save()
        return item

    @myhandler
    def get_all(self):
        for item in self.model.select():
            yield item

    @myhandler
    def delete_by_id(self, item_id: int) -> None:
        self.model.delete_by_id(item_id)

    @myhandler
    def get(self, **kwargs):
        return self.model.get(**kwargs)