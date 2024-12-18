from hmtc.domains.channel import Channel
from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository

testing_channel_dict = {
    "id": 101,
    "title": "Some Test Channel Title",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "1234adhjgfhjfaewr",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


def test_empty_channel(empty_db):
    c = Channel()
    assert type(c.model) == ChannelModel
    assert type(c.repo) == Repository
    assert c.model.id is None


def test_channel_create_and_load(empty_db):
    created_channel = Channel.create(testing_channel_dict)
    assert created_channel.title == testing_channel_dict["title"]
    assert created_channel.url == testing_channel_dict["url"]
    assert created_channel.youtube_id == testing_channel_dict["youtube_id"]
    assert created_channel.auto_update == testing_channel_dict["auto_update"]
    assert (
        str(created_channel.last_update_completed)
        == testing_channel_dict["last_update_completed"]
    )
    assert created_channel.id > 0
    loaded_channel = Channel.load(created_channel.id)
    assert loaded_channel.title == testing_channel_dict["title"]
    assert loaded_channel.url == testing_channel_dict["url"]
    assert loaded_channel.youtube_id == testing_channel_dict["youtube_id"]
    assert loaded_channel.auto_update == testing_channel_dict["auto_update"]
    assert (
        str(loaded_channel.last_update_completed)
        == testing_channel_dict["last_update_completed"]
    )
    Channel.delete_id(created_channel.id)


def test_channel_delete(seeded_db):
    created_channel = Channel().create(testing_channel_dict)
    Channel.delete_id(created_channel.id)
    c = ChannelModel.select().where(ChannelModel.id == created_channel.id).get_or_none()
    assert c is None


def test_serialize(seeded_db):
    new_id = Channel.create(testing_channel_dict)
    s = Channel.serialize(new_id)
    assert s["title"] == testing_channel_dict["title"]
    assert s["url"] == testing_channel_dict["url"]
    assert s["youtube_id"] == testing_channel_dict["youtube_id"]
    assert s["auto_update"] == testing_channel_dict["auto_update"]
    assert (
        str(s["last_update_completed"]) == testing_channel_dict["last_update_completed"]
    )
    Channel.delete_id(new_id)


def test_get_all(seeded_db):
    all_channels = Channel.get_all()
    assert len(list(all_channels)) == 2


def test_get_auto_update_channels(seeded_db):
    auto_update_channels = Channel.to_auto_update()
    assert len(list(auto_update_channels)) == 0


def test_update_channels(seeded_db):
    new_id = Channel.create(testing_channel_dict)
    channel = Channel.load(new_id)
    assert channel.title == testing_channel_dict["title"]
    Channel.update({"title": "A whole nother title", "id": new_id})
    assert ChannelModel.get_by_id(new_id).title == "A whole nother title"

    Channel.delete_id(new_id)
