from hmtc.domains.channel import Channel
from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository

ex_channel1 = {
    "title": "Harry Mack",
    "url": "https://www.youtube.com/channel/UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "youtube_id": "UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "auto_update": True,
    "last_update_completed": "2021-09-07 00:00:00",
}

ex_channel3 = {
    "title": "Beardyman",
    "url": "https://www.youtube.com/channel/UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "youtube_id": "fdsafUC59XppAqR0z5bGKj7Sw",
    "auto_update": False,
    "last_update_completed": "2020-09-07 00:00:00",
}


def test_empty_channel():
    c = Channel()
    assert type(c.model) == ChannelModel
    assert type(c.repo) == Repository
    assert c.model.id is None


def test_channel_create_and_load():
    created_channel = Channel().create(ex_channel1)
    assert created_channel.title == ex_channel1["title"]
    assert created_channel.url == ex_channel1["url"]
    assert created_channel.youtube_id == ex_channel1["youtube_id"]
    assert created_channel.auto_update == ex_channel1["auto_update"]
    assert (
        str(created_channel.last_update_completed)
        == ex_channel1["last_update_completed"]
    )
    assert created_channel.id > 0
    loaded_channel = Channel().load(created_channel.id)
    assert loaded_channel.title == ex_channel1["title"]
    assert loaded_channel.url == ex_channel1["url"]
    assert loaded_channel.youtube_id == ex_channel1["youtube_id"]
    assert loaded_channel.auto_update == ex_channel1["auto_update"]
    assert (
        str(loaded_channel.last_update_completed)
        == ex_channel1["last_update_completed"]
    )


def test_channel_delete():
    created_channel = Channel().create(ex_channel1)
    Channel.delete_id(created_channel.id)
    c = ChannelModel.select().where(ChannelModel.id == created_channel.id).get_or_none()
    assert c is None


def test_serialize():
    new_id = Channel.create(ex_channel1)
    s = Channel.serialize(new_id)
    assert s["title"] == ex_channel1["title"]
    assert s["url"] == ex_channel1["url"]
    assert s["youtube_id"] == ex_channel1["youtube_id"]
    assert s["auto_update"] == ex_channel1["auto_update"]
    assert s["last_update_completed"] == ex_channel1["last_update_completed"]


def test_get_all(channel_dict):
    Channel.create(ex_channel1)
    Channel.create(channel_dict)
    Channel.create(ex_channel3)
    all_channels = Channel.get_all()
    assert len(list(all_channels)) == 3


def test_get_auto_update_channels(channel_dict):
    Channel.create(ex_channel1)
    Channel.create(channel_dict)
    Channel.create(ex_channel3)
    auto_update_channels = Channel.to_auto_update()
    assert len(list(auto_update_channels)) == 2


def test_update_channels():
    new_id = Channel.create(ex_channel1)
    channel = Channel.load(new_id)
    assert channel.title == ex_channel1["title"]
    Channel.update({"title": "A whole nother title", "id": new_id})
    assert ChannelModel.get_by_id(new_id).title == "A whole nother title"


def test_last_update_completed(channel_dict):
    Channel.create(ex_channel1)
    Channel.create(channel_dict)
    Channel.create(ex_channel3)
    assert Channel.last_update_completed() == channel_dict["last_update_completed"]
