from hmtc.domains.channel import Channel
from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    channel_dict1,
    channel_dict2,
    channel_dict3,
    channel_item,
)


def test_empty_channel():
    c = Channel()
    assert type(c.model) == ChannelModel
    assert type(c.repo) == Repository
    assert c.model.id is None


def test_channel_create_and_load(channel_dict1):
    created_channel = Channel().create(channel_dict1)
    assert created_channel.title == channel_dict1["title"]
    assert created_channel.url == channel_dict1["url"]
    assert created_channel.youtube_id == channel_dict1["youtube_id"]
    assert created_channel.auto_update == channel_dict1["auto_update"]
    assert (
        str(created_channel.last_update_completed)
        == channel_dict1["last_update_completed"]
    )
    assert created_channel.id > 0
    loaded_channel = Channel().load(created_channel.id)
    assert loaded_channel.title == channel_dict1["title"]
    assert loaded_channel.url == channel_dict1["url"]
    assert loaded_channel.youtube_id == channel_dict1["youtube_id"]
    assert loaded_channel.auto_update == channel_dict1["auto_update"]
    assert (
        str(loaded_channel.last_update_completed)
        == channel_dict1["last_update_completed"]
    )


def test_channel_delete(channel_dict1):
    created_channel = Channel().create(channel_dict1)
    Channel.delete_id(created_channel.id)
    c = ChannelModel.select().where(ChannelModel.id == created_channel.id).get_or_none()
    assert c is None


def test_serialize(channel_dict1):
    new_id = Channel.create(channel_dict1)
    s = Channel.serialize(new_id)
    assert s["title"] == channel_dict1["title"]
    assert s["url"] == channel_dict1["url"]
    assert s["youtube_id"] == channel_dict1["youtube_id"]
    assert s["auto_update"] == channel_dict1["auto_update"]
    assert str(s["last_update_completed"]) == channel_dict1["last_update_completed"]


def test_get_all(channel_dict1, channel_dict2, channel_dict3):
    Channel.create(channel_dict1)
    Channel.create(channel_dict2)
    Channel.create(channel_dict3)
    all_channels = Channel.get_all()
    assert len(list(all_channels)) == 3


def test_get_auto_update_channels(channel_dict1, channel_dict2, channel_dict3):
    Channel.create(channel_dict1)
    Channel.create(channel_dict2)
    Channel.create(channel_dict3)
    auto_update_channels = Channel.to_auto_update()
    assert len(list(auto_update_channels)) == 2


def test_update_channels(channel_dict1):
    new_id = Channel.create(channel_dict1)
    channel = Channel.load(new_id)
    assert channel.title == channel_dict1["title"]
    Channel.update({"title": "A whole nother title", "id": new_id})
    assert ChannelModel.get_by_id(new_id).title == "A whole nother title"


def test_last_update_completed(channel_dict1, channel_dict2, channel_dict3):
    Channel.create(channel_dict1)
    Channel.create(channel_dict2)
    Channel.create(channel_dict3)
    assert Channel.last_update_completed() == channel_dict2["last_update_completed"]


def test_channel_item(channel_item, channel_dict1):
    assert channel_item.title == channel_dict1["title"]
