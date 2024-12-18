from typing import List

from loguru import logger

from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel
from hmtc.models import User as UserModel
from hmtc.repos.base_repo import Repository


class User:
    repo = Repository(model=UserModel(), label="User")

    @classmethod
    def create(cls, data) -> UserModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> UserModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> UserModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[UserModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
