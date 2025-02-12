from typing import Any, Dict

from peewee import fn

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import SectionTopic as SectionTopicModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.topic_repo import TopicRepo


class Topic(BaseDomain):
    model = TopicModel
    repo = TopicRepo()

    def serialize(self) -> Dict[str, Any]:
        num_sections = (
            SectionTopicModel.select(fn.COUNT(SectionTopicModel.section_id))
            .where(SectionTopicModel.topic_id == self.instance.id)
            .scalar()
        )
        return {
            "id": self.instance.id,
            "text": self.instance.text,
            "num_sections": num_sections,
        }
