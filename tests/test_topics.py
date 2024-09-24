from hmtc.models import (
    Topic as TopicModel,
    Video as VideoModel,
    Section as SectionModel,
    SectionTopics as SectionTopicsModel,
)
from hmtc.schemas.section import Section as SectionItem


def test_topic():
    topic = TopicModel.create(text="test")
    assert topic is not None


def test_delete_topic():
    topic = TopicModel.create(text="test")
    topic.delete_instance()
    assert TopicModel.get_or_none(TopicModel.text == "test") is None


def test_section_topics():
    v = VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    sec = SectionModel.create(start=0, end=1000, video=v)
    topic = TopicModel.create(text="bottle")
    topic2 = TopicModel.create(text="orange")
    topic3 = TopicModel.create(text="supercalifragilisticexpialidocious")
    SectionTopicsModel.create(section=sec, topic=topic, order=1)
    SectionTopicsModel.create(section=sec, topic=topic2, order=2)
    SectionTopicsModel.create(section=sec, topic=topic3, order=3)
    assert len(sec.topics) == 3
    assert topic.sections == topic3.sections


def test_section_schemas():
    v = VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    sec1 = SectionModel.create(start=0, end=1000, video=v)
    sec2 = SectionModel.create(start=1500, end=8000, video=v)
    topic = TopicModel.create(text="bottle")
    topic2 = TopicModel.create(text="orange")
    topic3 = TopicModel.create(text="supercalifragilisticexpialidocious")
    SectionTopicsModel.create(section=sec1, topic=topic, order=1)
    SectionTopicsModel.create(section=sec1, topic=topic2, order=2)
    SectionTopicsModel.create(section=sec2, topic=topic3, order=1)
    SectionTopicsModel.create(section=sec2, topic=topic2, order=2)
    section_details = SectionItem.get_details_for_section(sec1.id)
    assert section_details["start"] == 0
    assert section_details["end"] == 1000
    assert len(section_details["topics"]) == 2
    assert section_details["topics"][0]["text"] == "bottle"

    section_details = SectionItem.get_details_for_section(sec2.id)
    assert section_details["start"] == 1500
    assert section_details["end"] == 8000
    assert len(section_details["topics"]) == 2
    assert section_details["topics"][0]["text"] == "supercalifragilisticexpialidocious"
