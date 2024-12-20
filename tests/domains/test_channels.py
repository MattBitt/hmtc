from unittest.mock import patch
from peewee import IntegrityError
from hmtc.domains import *
from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository


def test_channel_create_and_load(channel_dicts):
    cd = channel_dicts[0]
    created_channel = Channel.create(cd)
    assert created_channel.instance.title == cd["title"]
    assert created_channel.instance.url == cd["url"]
    assert created_channel.instance.youtube_id == cd["youtube_id"]
    assert created_channel.instance.auto_update == cd["auto_update"]
    assert created_channel.instance.id > 0

    loaded_channel = Channel(created_channel.instance.id)
    assert loaded_channel.instance.title == cd["title"]
    assert loaded_channel.instance.url == cd["url"]
    assert loaded_channel.instance.youtube_id == cd["youtube_id"]
    assert loaded_channel.instance.auto_update == cd["auto_update"]
    created_channel.delete_me()


def test_channel_create_no_title(channel_dicts):
    cd = channel_dicts[0]
    del cd["title"]
    try:
        Channel.create(cd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(channel_dicts):
    cd = channel_dicts[1]
    created_channel = Channel.create(cd)
    loaded_channel = Channel.get_by(id=created_channel.instance.id)
    assert loaded_channel.instance.title == cd["title"]
    assert loaded_channel.instance.url == cd["url"]
    assert loaded_channel.instance.youtube_id == cd["youtube_id"]
    assert loaded_channel.instance.auto_update == cd["auto_update"]
    created_channel.delete_me()


def test_get_by_title(channel_dicts):
    cd = channel_dicts[1]
    created_channel = Channel.create(cd)
    loaded_channel = Channel.get_by(title=created_channel.instance.title)
    assert loaded_channel.instance.title == cd["title"]
    assert loaded_channel.instance.url == cd["url"]
    assert loaded_channel.instance.youtube_id == cd["youtube_id"]
    assert loaded_channel.instance.auto_update == cd["auto_update"]
    created_channel.delete_me()


def test_select_where(channel_dicts):
    cd = channel_dicts[1]
    cd2 = channel_dicts[2]
    created_channel = Channel.create(cd)
    Channel.create(cd2)
    channels = Channel.select_where(
        title=created_channel.instance.title, url=created_channel.instance.url
    )
    assert len(channels) == 1
    channel_item = Channel(channels[0].id)
    assert channel_item.instance.title == cd["title"]
    loaded_channel = channels[0]
    assert loaded_channel.title == cd["title"]
    assert loaded_channel.url == cd["url"]
    assert loaded_channel.youtube_id == cd["youtube_id"]
    assert loaded_channel.auto_update == cd["auto_update"]
    created_channel.delete_me()


def test_update_channel(channel_dicts):
    # setup
    cd = channel_dicts[2]
    channel = Channel.create(cd)
    # test
    new_channel = channel.update({"title": "New Title"})

    # verify
    assert new_channel.instance.title == "New Title"

    channel_from_db = (
        ChannelModel.select().where(ChannelModel.id == channel.instance.id).get()
    )
    assert channel_from_db.title == "New Title"

    # teardown
    channel.delete_me()


def test_channel_delete(channel_dicts):
    cd = channel_dicts[1]
    created_channel = Channel.create(cd)
    created_channel.delete_me()
    c = (
        ChannelModel.select()
        .where(ChannelModel.id == created_channel.instance.id)
        .get_or_none()
    )
    assert c is None


def test_serialize(channel_dicts):
    # setup
    cd = channel_dicts[2]
    channel = Channel.create(cd)
    # tests
    s = channel.serialize()
    assert s["title"] == cd["title"]
    assert s["url"] == cd["url"]
    assert s["youtube_id"] == cd["youtube_id"]
    assert s["auto_update"] == cd["auto_update"]
    assert str(s["last_update_completed"]) == cd["last_update_completed"]
    # teardown
    channel.delete_me()


def test_count(channel_dicts):
    # setup
    cd1 = channel_dicts[0]
    cd2 = channel_dicts[1]
    cd3 = channel_dicts[2]

    # tests
    assert Channel.count() == 0
    Channel.create(cd1)
    Channel.create(cd2)
    Channel.create(cd3)
    assert Channel.count() == 3

    # teardown
    for channel_dict in channel_dicts:
        channel = Channel.get_by(title=channel_dict["title"])
        channel.delete_me()

    assert Channel.count() == 0
