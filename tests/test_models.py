import os
from pathlib import Path

import peewee
from loguru import logger
from hmtc.config import init_config
from hmtc.models import Channel, ChannelFile, Playlist, Series, Video, get_file_type

config = init_config()


def test_series():
    s, created = Series.get_or_create(
        name="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created is True
    assert s.name == "test"

    all_series = Series.select()
    assert all_series.count() > 1
    logger.debug(f"all_series.count() = {all_series.count()}")
    s.delete_instance()


# this test leaves a record in the database
def test_permanance_setup():
    s = Series.create(name="testing permanent record")
    assert s is not None


def test_permanance_execute():
    s = Series.get_or_none(Series.name == "testing permanent record")
    assert s is None


def test_channel():
    Channel.create_table()
    c, created = Channel.get_or_create(
        name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;"
    )
    assert c.name == "test"
    assert created is True

    c.delete_instance()


def test_playlist():
    Playlist.create_table()
    p, created = Playlist.get_or_create(
        title="test", url="www.yahoo.com/playlists", youtube_id="PLTvadsfadghas"
    )
    assert created is True
    assert p.title == "test"

    all_playlist = Playlist.select()
    # assert all_playlist.count()  > 1
    logger.debug(f"all_playlist.count() = {all_playlist.count()}")
    p.delete_instance()


def test_video():
    Video.create_table()
    v, created = Video.get_or_create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
        file_path="",
    )
    assert created is True
    assert v.title == "test"
    try:
        Video.create(title="test")

    except peewee.IntegrityError:

        assert len(Video.select()) == 1

    v3, created3 = Video.get_or_create(title="test")
    assert v3.title == "test"
    assert created3 is False
    assert len(Video.select()) == 1
    v.delete_instance()


def test_delete_series():
    s = Series.create(name="test")
    assert s is not None
    s.delete_instance()
    s2 = Series.get_or_none(Series.name == "test")
    assert s2 is not None
    assert s2.name == "test"
    assert s2.deleted_at is not None


def test_create_channel_file(test_files):
    target = Path(config["paths"]["working"]) / "test_file_output"

    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")

    assert c is not None

    for file in test_files:
        # with open(source / file, "rb") as src_file:
        #     f: FileInfo = {"name": file, "size": 100, "data": src_file.read()}

        new_name = target / file
        file_type = get_file_type(file)
        nf1 = ChannelFile(
            path=new_name.parent,
            filename=new_name,
            file_type=file_type,
            extension="asdf",
            channel=c,
        )
        assert nf1 is not None
        assert nf1.extension == "asdf"

        nf2 = ChannelFile.get_or_create(
            path=target,
            filename="some other name",
            file_type="poster",
            extension="asdffdsa",
            channel=c,
        )
        assert nf2 is not None
    # assert c.files.count() == len(test_files) + 1
    for f in c.files:
        logger.debug(f"{f.filename}")
    c.delete_instance()


def test_add_poster_to_channel(test_image_filename):
    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")

    c.add_file(test_image_filename)
    assert c.files.count() == 1
