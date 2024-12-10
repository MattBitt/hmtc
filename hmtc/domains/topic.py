from typing import List

from loguru import logger

from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopic as SectionTopicsModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository


class Topic:
    repo = Repository(model=TopicModel(), label="Topic")
    section_topics_repo = Repository(model=SectionTopicsModel(), label="SectionTopics")

    @classmethod
    def create(cls, data) -> TopicModel:
        new_topic = cls.repo.create_item(data=data)
        return new_topic

    @classmethod
    def load(cls, item_id) -> TopicModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> TopicModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[TopicModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        sts = SectionTopicsModel.select().where(SectionTopicsModel.topic == item_id)
        for st in sts:
            cls.section_topics_repo.delete_by_id(st.id)
        cls.repo.delete_by_id(item_id=item_id)
