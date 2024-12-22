from pathlib import Path
from unittest.mock import patch

from peewee import IntegrityError

from hmtc.domains.channel import Channel
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

    loaded_channel = Channel.load(created_channel.instance.id)
    assert loaded_channel.instance.title == cd["title"]
    assert loaded_channel.instance.url == cd["url"]
    assert loaded_channel.instance.youtube_id == cd["youtube_id"]
    assert loaded_channel.instance.auto_update == cd["auto_update"]
    created_channel.delete()


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
    created_channel.delete()


def test_get_by_title(channel_dicts):
    cd = channel_dicts[1]
    created_channel = Channel.create(cd)
    loaded_channel = Channel.get_by(title=created_channel.instance.title)
    assert loaded_channel.instance.title == cd["title"]
    assert loaded_channel.instance.url == cd["url"]
    assert loaded_channel.instance.youtube_id == cd["youtube_id"]
    assert loaded_channel.instance.auto_update == cd["auto_update"]
    created_channel.delete()


def test_select_where(channel_dicts):
    # setup
    cd1 = channel_dicts[1]
    cd2 = channel_dicts[2]
    channel1 = Channel.create(cd1)
    channel2 = Channel.create(cd2)

    # tests
    channels_query = Channel.select_where(
        title=channel1.instance.title, url=channel1.instance.url
    )
    assert len(channels_query) == 1
    channel_item = Channel(channels_query[0].instance.id)
    assert channel_item.instance.title == cd1["title"]
    loaded_channel = channels_query[0]
    assert loaded_channel.instance.title == cd1["title"]
    assert loaded_channel.instance.url == cd1["url"]
    assert loaded_channel.instance.youtube_id == cd1["youtube_id"]
    assert loaded_channel.instance.auto_update == cd1["auto_update"]
    # teardown
    channel1.delete()
    channel2.delete()


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
    channel.delete()


def test_channel_delete(channel_dicts):
    cd = channel_dicts[1]
    created_channel = Channel.create(cd)
    created_channel.delete()
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
    channel.delete()


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
        channel.delete()

    assert Channel.count() == 0


def test_file_count_no_files(channel_dicts):
    # setup
    cd = channel_dicts[0]
    channel = Channel.create(cd)

    # tests
    assert channel.fm.count() == 0

    # teardown
    channel.delete()


def test_file_count_with_files(channel_dicts):
    # setup
    cd = channel_dicts[0]
    channel = Channel.create(cd)
    info_file = Path("info.json")
    with info_file.open("w") as f:
        f.write("test")
    channel.fm.add_file(channel.instance, info_file)

    # tests
    assert channel.fm.count() == 1
    # teardown
    channel.delete_me()


def test_channel_files(channel_dicts):
    # setup
    cd = channel_dicts[0]
    channel = Channel.create(cd)
    info_file = Path("info.json")
    with info_file.open("w") as f:
        f.write("test")

    channel.fm.add_file(channel.instance, info_file)
    # tests
    files = channel.fm.files(channel.instance.id)
    assert len(files) == 1
    assert "info.json" in files[0].name
    serialized = channel.serialize()
    assert len(serialized["files"]) == 1
    assert "info" in serialized["files"]
    # teardown
    channel.delete_me()


def test_download_files(channel_dicts, tmp_path):
    # setup
    cd = channel_dicts[0]
    channel = Channel.create(cd)
    file = tmp_path / "someyoutube_id_info.json"
    file.touch()
    # tests
    with patch("hmtc.domains.channel.download_channel_files") as mock_download:
        mock_download.return_value = [file]
        channel.download_files()
        files = channel.fm.files(channel.instance.id)
        assert len(files) == 1
        assert "info.json" in files[0].name
    # teardown
    channel.delete_me()
    mock_download.assert_called_once_with(
        channel.instance.youtube_id, channel.instance.url
    )
