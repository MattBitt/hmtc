from loguru import logger

from hmtc.config import init_config
from hmtc.models import BaseModel
from hmtc.decorators import myhandler

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
    def update_item(self, item_id, data) -> BaseModel:
        self.load_item(item_id).update(**data).execute()
        return self.load_item(item_id)

    @myhandler
    def get_all(self):
        for item in self.model.select():
            yield item

    @myhandler
    def delete_by_id(self, item_id: int):
        self.model.delete_by_id(item_id)
