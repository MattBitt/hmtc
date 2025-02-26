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

    def my_title(self):
        if self.instance.title is not None:
            return self.instance.title
        _topics = [t.instance.text for t in self.topics()]
        if len(_topics) > 0:
            return ",".join(_topics)[:40]

        if self.instance.comments is not None:
            return self.instance.comments[:40]
        raise ValueError(f"Can't create a title without some info in the section.")

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
        if topic == "":
            # this occurs due to the reactive text box being cleared
            # probably a good way to avoid it, but i'm just
            # returning None
            return None
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

    def remove_topic(self, topic):
        section_id = self.instance.id
        logger.debug(f"remove_topic: {topic} from seciton {section_id}")

        t = TopicModel.select().where(TopicModel.text == topic).get_or_none()
        if t is None:
            logger.error(f"Topic {topic} not found")
            return

        SectionTopicModel.delete().where(
            (SectionTopicModel.section_id == section_id)
            & (SectionTopicModel.topic_id == t.id)
        ).execute()

        topic_still_needed = SectionTopicModel.get_or_none(
            SectionTopicModel.topic_id == t.id
        )
        if topic_still_needed is None:
            logger.debug(f"Topic no longer needed {t.text} ({t.id}). Removing.")
            t.delete_instance()

        logger.error(f"Removed topic {t.text} ({t.id}) from section {section_id}")

    def num_topics(self):
        return (
            TopicModel.select()
            .join(SectionTopicModel, on=(TopicModel.id == SectionTopicModel.topic_id))
            .where(SectionTopicModel.section_id == self.instance.id)
            .count()
        )

    def topics_serialized(self):
        return [t.serialize() for t in self.topics()]

    def topics(self):
        from hmtc.domains.topic import Topic

        _topics = (
            TopicModel.select()
            .join(SectionTopicModel, on=(TopicModel.id == SectionTopicModel.topic_id))
            .where(SectionTopicModel.section_id == self.instance.id)
            .order_by(SectionTopicModel.order)
        )
        return [Topic(t) for t in _topics]
