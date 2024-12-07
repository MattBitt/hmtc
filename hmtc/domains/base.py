from dataclasses import asdict, dataclass, field

from loguru import logger

from hmtc.config import init_config
from hmtc.models import BaseModel

config = init_config()


class Repository:

    @staticmethod
    def load_by_id(model, _id: int) -> BaseModel:
        try:
            _item = model.get_by_id(_id)
        except Exception as e:
            logger.error(f"Error {e} loading with id {_id}")
            raise e

        return _item

    @staticmethod
    def create_from_dict(model, data) -> BaseModel:
        try:
            _item = model.create(**data)
        except Exception as e:
            logger.error(f"Error {e} creating with {data}")
            raise e

        return _item

    @staticmethod
    def update_from_dict(model, _id, data) -> BaseModel:
        try:
            _item = model.get_by_id(_id)
            new_item = _item.update(**data).execute()
        except Exception as e:
            logger.error(f"Error {e} updating with {data}")
            raise e

        return new_item

    @staticmethod
    def get_all(model):
        for item in model.select():
            yield item

    @staticmethod
    def delete_by_id(model, _id: int):
        model.delete_by_id(_id)
