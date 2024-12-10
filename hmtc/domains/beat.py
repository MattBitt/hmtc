from typing import List

from loguru import logger

from hmtc.domains.section import Section
from hmtc.models import Beat as BeatModel
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository


class Beat:
    repo = Repository(model=BeatModel(), label="Beat")

    @classmethod
    def create(cls, data) -> BeatModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> BeatModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> BeatModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[BeatModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
