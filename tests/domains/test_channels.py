from unittest.mock import patch

from hmtc.domains import *
from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository


def test_empty_channel(empty_db):
    c = Channel()
    assert type(c.model) == type(ChannelModel)
    assert type(c.repo) == Repository


def test_channel_create_and_load(empty_db, channel_dict):
    created_channel = Channel.create(channel_dict)
    assert created_channel.instance.title == channel_dict["title"]
    assert created_channel.instance.url == channel_dict["url"]
    assert created_channel.instance.youtube_id == channel_dict["youtube_id"]
    assert created_channel.instance.auto_update == channel_dict["auto_update"]
    assert (
        str(created_channel.last_update_completed())
        == channel_dict["last_update_completed"]
    )
    assert created_channel.instance.id > 0
    loaded_channel = Channel(created_channel.instance.id)
    assert loaded_channel.instance.title == channel_dict["title"]
    assert loaded_channel.instance.url == channel_dict["url"]
    assert loaded_channel.instance.youtube_id == channel_dict["youtube_id"]
    assert loaded_channel.instance.auto_update == channel_dict["auto_update"]
    assert (
        str(loaded_channel.last_update_completed())
        == channel_dict["last_update_completed"]
    )
    created_channel.delete_me()


def test_channel_delete(seeded_db, channel_dict):
    created_channel = Channel.create(channel_dict)
    Channel.delete_id(created_channel.id)
    c = ChannelModel.select().where(ChannelModel.id == created_channel.id).get_or_none()
    assert c is None


def test_serialize(seeded_db, channel_dict):
    new_id = Channel.create(channel_dict)
    s = Channel.serialize(new_id)
    assert s["title"] == channel_dict["title"]
    assert s["url"] == channel_dict["url"]
    assert s["youtube_id"] == channel_dict["youtube_id"]
    assert s["auto_update"] == channel_dict["auto_update"]
    assert str(s["last_update_completed"]) == channel_dict["last_update_completed"]
    Channel.delete_id(new_id)


def test_get_all(seeded_db):
    all_channels = Channel.get_all()
    assert len(list(all_channels)) == 2
