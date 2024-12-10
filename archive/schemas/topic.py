from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.models import SectionTopic as SectionTopicsModel
from hmtc.models import Topic as TopicModel


@dataclass(frozen=True, order=True, kw_only=True)
class Topic:

    text: str
    item_type: str = "TOPIC"
    id: int = 0
    sections: list = field(default_factory=list)

    def from_model(topic: TopicModel) -> "Topic":
        return Topic(
            id=topic.id,
            text=topic.text,
            sections=[x.section for x in topic.sections],
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "section_count": len(self.sections),
        }

    @staticmethod
    def update_from_dict(item_id, new_data):
        logger.debug(f"Updating Topic {item_id} with {new_data}")
        topic = TopicModel.get_by_id(item_id)
        topic.text = new_data["text"]
        topic.save()
        return Topic.from_model(topic)

    @staticmethod
    def delete_id(item_id):
        logger.debug(f"Deleting Topic {item_id}")
        topic = TopicModel.get_by_id(item_id)
        section_topics = SectionTopicsModel.select().where(
            SectionTopicsModel.topic == topic
        )
        for st in section_topics:
            st.delete_instance()

        topic.delete_instance()
