from typing import List
import peewee
from loguru import logger

from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopic as SectionTopicModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Topic as TopicModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


class Section:
    repo = Repository(model=SectionModel(), label="Section")
    video_repo = Repository(model=VideoModel(), label="Video")
    track_repo = Repository(model=TrackModel(), label="Track")
    topic_repo = Repository(model=TopicModel(), label="Topic")

    @classmethod
    def create(cls, data) -> SectionModel:
        video = cls.video_repo.get(id=data["video_id"])
        data["video"] = video

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SectionModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> SectionModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SectionModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        from hmtc.domains.topic import Topic

        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["video"] = Video.serialize(item.video.id)
        _dict["topics"] = [Topic.serialize(topic.id) for topic in item.topics]
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        this_section = cls.load(item_id)

        if this_section.track:
            _track = this_section.track.get()
            cls.track_repo.delete_by_id(item_id=_track.id)

        if len(this_section.topics) > 0:
            logger.debug(
                f"Deleting topics for section {item_id} {len(this_section.topics)}"
            )
            for topic in this_section.topics:
                cls.remove_topic(section_id=item_id, topic_id=topic.id)

        sc_segments = SuperchatSegmentModel.select().where(
            SuperchatSegmentModel.section_id == item_id
        )
        for sc_segment in sc_segments:
            SuperchatSegmentModel.delete_by_id(sc_segment.id)

        cls.repo.delete_by_id(item_id=item_id)

    @classmethod
    def load_for_video(cls, video_id) -> List[SectionModel]:
        sections = SectionModel.select().where(SectionModel.video_id == video_id)
        return [Section.load(section.id) for section in sections]

    @classmethod
    def add_topic(cls, section_id, topic_dict):
        topic, created = cls.topic_repo.load_or_create_item(topic_dict)
        try:
            SectionTopicModel.create(section_id=section_id, topic_id=topic.id, order=1)
        except Exception as e:
            logger.error(e)
            raise

    @classmethod
    def remove_topic(cls, section_id, topic_id):
        try:
            SectionTopicModel.delete().where(
                SectionTopicModel.section_id == section_id,
                SectionTopicModel.topic_id == topic_id,
            ).execute()
        except Exception as e:
            logger.error(e)
            raise
        # need to delete topic if its unused
        unused_topics = TopicModel.select().join(
            SectionTopicModel, peewee.JOIN.LEFT_OUTER
        )
