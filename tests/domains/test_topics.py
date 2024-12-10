import pytest

from hmtc.domains.topic import Topic
from hmtc.models import Section as SectionModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    section_item,
    series_item,
    topic_dict1,
    topic_dict2,
    topic_dict3,
    topic_item,
    video_item,
    youtube_series_item,
)


def test_empty_topic():
    c = Topic()
    assert type(c.repo) == Repository


def test_topic_create_and_load(
    topic_dict1,
):
    created_topic = Topic.create(topic_dict1)
    assert created_topic.text == topic_dict1["text"]
    assert created_topic.id > 0

    loaded_topic = Topic.load(created_topic.id)
    assert loaded_topic.text == topic_dict1["text"]


def test_topic_delete(video_item, topic_item):

    Topic.delete_id(topic_item.id)
    t = TopicModel.select().where(TopicModel.id == topic_item.id).get_or_none()
    assert t is None


def test_serialize(topic_item, video_item, section_item):
    t = Topic.serialize(topic_item.id)
    assert t["text"] == topic_item.text
    assert t["id"] == topic_item.id


def test_get_all(topic_item):
    all_topics = Topic.get_all()
    assert len(list(all_topics)) == 1


def test_update_topics(topic_item):
    topic = Topic.load(topic_item.id)
    assert topic.text == topic_item.text
    Topic.update({"text": "antidis", "id": topic_item.id})
    assert TopicModel.get_by_id(topic_item.id).text == "antidis"
