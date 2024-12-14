import pytest

from hmtc.domains.section import Section
from hmtc.domains.topic import Topic
from hmtc.models import Section as SectionModel
from hmtc.models import Topic as TopicModel
from hmtc.repos.base_repo import Repository

testing_topic_dict = {
    "id": 40567,
    "text": "Some Test Topic",
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
    _topic = TopicModel.select().first()
    topic = Topic.serialize(_topic.id)
    assert topic["text"] == _topic.text
    assert topic["id"] == _topic.id


def test_get_all(seeded_db):
    all_topics = Topic.get_all()
    assert len(list(all_topics)) == 6


def test_update_topics(seeded_db):
    TOPIC_ID = 1
    topic = Topic.load(TOPIC_ID)
    orig_text = topic.text
    assert topic.text == "apple"
    Topic.update({"text": "A whole nother text", "id": 1})
    assert TopicModel.get_by_id(TOPIC_ID).text == "A whole nother text"
    Topic.update({"text": orig_text, "id": TOPIC_ID})
    assert TopicModel.get_by_id(TOPIC_ID).text == orig_text


def test_section_add_topic(seeded_db):
    section = SectionModel.select().first()
    _topic = TopicModel.select().first()
    section_id = section.id
    topic_dict = {"id": 123, "text": "blueberry"}
    num_topics = len(section.topics)
    Section.add_topic(section_id, topic_dict)
    assert len(section.topics) == num_topics + 1
    Section.add_topic(section_id, Topic.serialize(_topic.id))
    assert len(section.topics) == num_topics + 2
