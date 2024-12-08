from typing import List

from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.repos.base_repo import Repository


class Album:
    repo = Repository(model=AlbumModel(), label="Album")

    @classmethod
    def create(cls, data) -> AlbumModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> AlbumModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> AlbumModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[AlbumModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["release_date"] = str(_dict["release_date"])

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
