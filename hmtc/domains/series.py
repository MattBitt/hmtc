from typing import List

from loguru import logger

from hmtc.repos.base_repo import Repository
from hmtc.models import Series as SeriesModel


class Series:
    model = SeriesModel()
    repo = Repository(model=model, label="Series")

    @classmethod
    def create(cls, data) -> SeriesModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SeriesModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> SeriesModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SeriesModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        return item.my_dict()

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
