from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.models import Topic as TopicModel


@dataclass(frozen=True, order=True)
class Topic:

    text: str
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
