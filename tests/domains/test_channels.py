from hmtc.domains.channel import Channel
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
    "last_update_completed": None,
}


def test_base_method():
    c = Channel.create_from_dict(ex_channel1)
    assert c.some_method() == "No data supplied"


def test_channel_create():
    new_c = Channel.create_from_dict(ex_channel1)
    assert new_c.channel.title == ex_channel1["title"]
    assert new_c.channel.url == ex_channel1["url"]
    assert new_c.channel.youtube_id == ex_channel1["youtube_id"]
    assert new_c.channel.auto_update == ex_channel1["auto_update"]
    assert (
        str(new_c.channel.last_update_completed) == ex_channel1["last_update_completed"]
    )
    channel_in_db = ChannelModel.get_by_id(new_c.channel.id)
    assert channel_in_db.title == ex_channel1["title"]
    assert channel_in_db.url == ex_channel1["url"]
    assert channel_in_db.youtube_id == ex_channel1["youtube_id"]
    assert channel_in_db.auto_update == ex_channel1["auto_update"]
    assert (
        str(channel_in_db.last_update_completed) == ex_channel1["last_update_completed"]
    )


def test_channel_delete():
    new_c = Channel.create_from_dict(ex_channel1)
    assert new_c.channel.title == ex_channel1["title"]
    _id = new_c.channel.id
    new_c.delete_me()
    assert ChannelModel.get_or_none(ChannelModel.id == _id) is None


def test_serialize():
    new_c = Channel.create_from_dict(ex_channel1)
    s = new_c.serialize()
    assert s.title == ex_channel1["title"]
    assert s.url == ex_channel1["url"]
    assert s.youtube_id == ex_channel1["youtube_id"]
    assert s.auto_update == ex_channel1["auto_update"]
    assert s.last_update_completed == ex_channel1["last_update_completed"]


def test_get_all():
    Channel.create_from_dict(ex_channel1)
    Channel.create_from_dict(ex_channel2)
    Channel.create_from_dict(ex_channel3)
    all_channels = Channel.get_all()
    assert len(list(all_channels)) == 3


def test_get_auto_update_channels():
    Channel.create_from_dict(ex_channel1)
    Channel.create_from_dict(ex_channel2)
    Channel.create_from_dict(ex_channel3)
    auto_update_channels = Channel.get_auto_update_channels()
    assert len(list(auto_update_channels)) == 2
