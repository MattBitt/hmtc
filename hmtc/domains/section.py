from typing import Any, Dict

from loguru import logger

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopic as SectionTopicModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.section_repo import SectionRepo


class Section(BaseDomain):
    model = SectionModel
    repo = SectionRepo()

    def serialize(self) -> Dict[str, Any]:
        topics = self.topics_serialized()
        return {
            "id": self.instance.id,
            "start": self.instance.start,
            "end": self.instance.end,
            "section_type": self.instance.section_type,
            "video_id": self.instance.video_id,
            "topics": topics,
        }

    @classmethod
    def get_for_video(cls, video_id):
        return [
            cls(s)
            for s in SectionModel.select().where(SectionModel.video_id == video_id)
        ]

    def delete(self):
        secttopics = SectionTopicModel.select().where(
            SectionTopicModel.section_id == self.instance.id
        )
        for st in secttopics:
            if len(st.topic.sections) == 1:
                t = st.topic
                t.delete_instance()
            else:
                st.delete_instance()

        self.instance.delete_instance()

    def add_topic(self, topic: str):
        section_number = self.num_topics() + 1
        topic, created = TopicModel.get_or_create(text=topic)
        existing = (
            SectionTopicModel.select()
            .where(
                (SectionTopicModel.section_id == self.instance.id)
                & (SectionTopicModel.topic_id == topic.id)
            )
            .get_or_none()
        )
        if existing:
            logger.error(f"This section already exists. Skipping creation")
            return
        st = SectionTopicModel.create(
            section_id=self.instance.id, topic_id=topic.id, order=section_number
        )
        return st

    def remove_topic(self, topic_id):
        topic = TopicModel.get_by_id(topic_id)
        topic.delete_instance()

    def num_topics(self):
        return (
            TopicModel.select()
            .join(SectionTopicModel, on=(TopicModel.id == SectionTopicModel.topic_id))
            .where(SectionTopicModel.section_id == self.instance.id)
            .count()
        )

    def topics_serialized(self):
        from hmtc.domains.topic import Topic

        _topics = (
            TopicModel.select()
            .join(SectionTopicModel, on=(TopicModel.id == SectionTopicModel.topic_id))
            .where(SectionTopicModel.section_id == self.instance.id)
            .order_by(SectionTopicModel.order)
        )
        return [Topic(t).serialize() for t in _topics]
