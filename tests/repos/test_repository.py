from hmtc.models import Channel as ChannelModel
from hmtc.repos.base_repo import Repository


testing_channel_dict = {
    "id": 867,
    "title": "Some Test Channel Title",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "1234adfvcxzadsr",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


def test_repository():
    repo = Repository(model=ChannelModel, label="Channel")
    assert repo.model == ChannelModel
    assert repo.label == "Channel"


def test_create_and_load_from_dict(seeded_db):
    repo = Repository(model=ChannelModel, label="Channel")
    item = repo.create_item(testing_channel_dict)
    assert item.id > 0
    assert item.title == testing_channel_dict["title"]
    assert item.url == testing_channel_dict["url"]
    assert item.youtube_id == testing_channel_dict["youtube_id"]
    assert item.auto_update == testing_channel_dict["auto_update"]
    assert (
        str(item.last_update_completed) == testing_channel_dict["last_update_completed"]
    )

    loaded_item = repo.load_item(item.id)
    assert loaded_item.title == testing_channel_dict["title"]
    assert loaded_item.url == testing_channel_dict["url"]
    assert loaded_item.youtube_id == testing_channel_dict["youtube_id"]
    assert loaded_item.auto_update == testing_channel_dict["auto_update"]
    assert (
        str(loaded_item.last_update_completed)
        == testing_channel_dict["last_update_completed"]
    )
    repo.delete_by_id(item.id)


def test_load_with_bad_id(seeded_db):
    repo = Repository(model=ChannelModel, label="Channel")
    try:
        item = repo.load_item(999999)
        assert False
    except Exception as e:
        assert True


def test_update_from_dict(seeded_db):
    repo = Repository(model=ChannelModel, label="Channel")
    new_item = repo.create_item(testing_channel_dict)
    assert new_item.id > 0
    updated_item = repo.update_item({"title": "New Title - Line 42", "id": new_item.id})
    assert updated_item.title == "New Title - Line 42"
