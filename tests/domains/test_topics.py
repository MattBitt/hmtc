import pytest

from hmtc.domains.section import Section
from hmtc.domains.topic import Topic
from hmtc.models import Section as SectionModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository

testing_topic_dict = {
    "text": "apple",
}


def test_empty_topic():
    c = Topic()
    assert type(c.repo) == Repository


def test_topic_create_and_load(
    seeded_db,
):
    created_topic = Topic.create(testing_topic_dict)
    assert created_topic.text == testing_topic_dict["text"]
    assert created_topic.id > 0

    loaded_topic = Topic.load(created_topic.id)
    assert loaded_topic.text == testing_topic_dict["text"]
    Topic.delete_id(created_topic.id)


def test_topic_delete(seeded_db):
    new_topic = Topic.create(testing_topic_dict)
    Topic.delete_id(new_topic.id)


def test_serialize(seeded_db):
    _topic = Topic.create(testing_topic_dict)
    topic = Topic.serialize(_topic.id)
    assert topic["text"] == _topic.text
    assert topic["id"] == _topic.id

    Topic.delete_id(_topic.id)


def test_get_all(seeded_db):
    all_topics = Topic.get_all()
    assert len(list(all_topics)) == 0


def test_update_topics(seeded_db):
    topic = Topic.create(testing_topic_dict)
    orig_text = topic.text
    assert topic.text == "apple"
    Topic.update({"text": "A whole nother text", "id": topic.id})
    assert TopicModel.get_by_id(topic.id).text == "A whole nother text"
    Topic.update({"text": orig_text, "id": topic.id})
    assert TopicModel.get_by_id(topic.id).text == orig_text
    Topic.delete_id(topic.id)
