import pytest
from hmtc.domains.topic import Topic
from hmtc.models import Topic as TopicModel


def test_topic_create_and_load(topic_dicts):
    td = topic_dicts[0]
    created_topic = Topic.create(td)

    assert created_topic.instance.text == td["text"]
    assert created_topic.instance.id > 0

    loaded_topic = Topic.load(created_topic.instance.id)
    assert loaded_topic.instance.text == td["text"]
    created_topic.delete()


def test_topic_create_no_text(topic_dicts):
    td = topic_dicts[0]
    del td["text"]
    try:
        Topic.create(td)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)


def test_get_by_id(topic_item):
    loaded_topic = Topic.get_by(id=topic_item.instance.id)
    assert loaded_topic.instance.text == topic_item.instance.text


def test_get_by_text(topic_item):
    loaded_topic = Topic.get_by(text=topic_item.instance.text)
    assert loaded_topic.instance.text == topic_item.instance.text


def test_select_where(topic_item):
    topic_query = Topic.select_where(text=topic_item.instance.text)
    assert len(topic_query) == 1
    topic = topic_query[0]
    assert topic.instance.text == topic_item.instance.text


def test_update_topic(topic_item):
    topic = topic_item
    new_topic = topic.update({"text": "Updated Text"})
    assert new_topic.instance.text == "Updated Text"

    topic_from_db = TopicModel.select().where(TopicModel.id == topic.instance.id).get()
    assert topic_from_db.text == "Updated Text"


def test_topic_delete(topic_item):
    topic = topic_item
    topic.delete()
    t = TopicModel.select().where(TopicModel.id == topic_item.instance.id).get_or_none()
    assert t is None


def test_serialize(topic_item):
    t = topic_item.serialize()
    assert t["text"] == topic_item.instance.text
