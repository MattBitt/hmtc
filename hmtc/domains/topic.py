from typing import List

from loguru import logger

from hmtc.domains.section import Section
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopics as SectionTopicsModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository


class Topic:
    repo = Repository(model=TopicModel(), label="Topic")
    section_repo = Repository(model=SectionModel(), label="Section")
    section_topics_repo = Repository(model=SectionTopicsModel(), label="SectionTopics")

    @classmethod
    def create(cls, data) -> TopicModel:
        section = cls.section_repo.get(id=data["section"])
        data["section"] = section
        new_topic = cls.repo.create_item(data=data)
        cls.section_topics_repo.create_item(
            data={"section": section, "topic": new_topic, "order": 1}
        )
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
        _dict["sections"] = [Section.serialize(sect.id) for sect in item.sections]
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        sts = SectionTopicsModel.select().where(SectionTopicsModel.topic == item_id)
        for st in sts:
            cls.section_topics_repo.delete_by_id(st.id)
        cls.repo.delete_by_id(item_id=item_id)
