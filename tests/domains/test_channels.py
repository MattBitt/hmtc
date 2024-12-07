from hmtc.domains.channel import Channels
from hmtc.models import Channel as ChannelModel

ex_channel1 = {
    "title": "Harry Mack",
    "url": "https://www.youtube.com/channel/UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "youtube_id": "UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "auto_update": True,
    "last_update_completed": "2021-09-07 00:00:00",
}
ex_channel2 = {
    "title": "Harry Mack Clips",
    "url": "https://www.youtube.com/channel/UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "youtube_id": "vcxzvUC59Xp4Qe0pAqRGKj7Sw",
    "auto_update": True,
    "last_update_completed": "2022-09-07 00:00:00",
}
ex_channel3 = {
    "title": "Beardyman",
    "url": "https://www.youtube.com/channel/UC59Xp4Qe0pAqR0z5bGKj7Sw",
    "youtube_id": "fdsafUC59XppAqR0z5bGKj7Sw",
    "auto_update": False,
    "last_update_completed": "2020-09-07 00:00:00",
}


def test_empty_channels():
    c = Channels()
    assert c.model is not None
    assert c.model_verbose == "Channel"


def test_channel_create():
    c = Channels()
    new_channel = c.create(ex_channel1)
    assert new_channel.model.title == ex_channel1["title"]
    assert new_channel.model.url == ex_channel1["url"]
    assert new_channel.model.youtube_id == ex_channel1["youtube_id"]
    assert new_channel.model.auto_update == ex_channel1["auto_update"]
    assert (
        str(new_channel.model.last_update_completed)
        == ex_channel1["last_update_completed"]
    )
    channel_in_db = ChannelModel.get_by_id(new_channel.model.id)
    assert channel_in_db.title == ex_channel1["title"]
    assert channel_in_db.url == ex_channel1["url"]
    assert channel_in_db.youtube_id == ex_channel1["youtube_id"]
    assert channel_in_db.auto_update == ex_channel1["auto_update"]
    assert (
        str(channel_in_db.last_update_completed) == ex_channel1["last_update_completed"]
    )


def test_channel_delete():
    new_c = Channels().create(ex_channel1)
    assert new_c.model.title == ex_channel1["title"]
    _id = new_c.model.id
    new_c.delete_me()
    c = ChannelModel.select().where(ChannelModel.id == _id).get_or_none()
    assert c is None


def test_serialize():
    new_c = Channels().create(ex_channel1)
    s = new_c.serialize()
    assert s["title"] == ex_channel1["title"]
    assert s["url"] == ex_channel1["url"]
    assert s["youtube_id"] == ex_channel1["youtube_id"]
    assert s["auto_update"] == ex_channel1["auto_update"]
    assert s["last_update_completed"] == ex_channel1["last_update_completed"]


def test_get_all():
    Channels().create(ex_channel1)
    Channels().create(ex_channel2)
    Channels().create(ex_channel3)
    all_channels = Channels().get_all()
    assert len(list(all_channels)) == 3


def test_get_auto_update_channels():
    Channels().create(ex_channel1)
    Channels().create(ex_channel2)
    Channels().create(ex_channel3)
    auto_update_channels = Channels().to_auto_update()
    assert len(list(auto_update_channels)) == 2


def test_update_channels():
    channel = Channels().create(ex_channel1)
    _id = channel.model.id
    assert channel.model.title == ex_channel1["title"]
    channel.update({"title": "A whole nother title"})
    assert ChannelModel.get_by_id(_id).title == "A whole nother title"


def test_last_update_completed():
    Channels().create(ex_channel1)
    Channels().create(ex_channel2)
    Channels().create(ex_channel3)
    assert Channels().last_update_completed() == ex_channel2["last_update_completed"]
