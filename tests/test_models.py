from pathlib import Path

import peewee
import pytest
from loguru import logger

from hmtc.config import init_config
from hmtc.db import seed_database
from hmtc.models import (
    Channel,
    File,
    Playlist,
    Section,
    Series,
    get_file_type,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Video as VideoModel,
)

config = init_config()


def test_empty_db():
    assert len(Playlist.select()) == 0
    assert len(Channel.select()) == 0
    assert len(Series.select()) == 0
    assert len(VideoModel.select()) == 0
    assert len(File.select()) == 0
    assert len(Section.select()) == 0


def test_seed_database():
    seed_database()
    assert len(Channel.select()) > 0
    assert len(Playlist.select()) > 0

    assert len(Series.select()) > 0


def test_series():
    s, created = Series.get_or_create(
        name="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created == True
    assert s.name == "test"

    all_series = Series.select()
    assert all_series.count() == 1
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
    assert created == True

    c.delete_instance()


def test_playlist():
    Playlist.create_table()
    p, created = Playlist.get_or_create(
        title="test", url="www.yahoo.com/playlists", youtube_id="PLTvadsfadghas"
    )
    assert created == True
    assert p.title == "test"

    all_playlist = Playlist.select()
    # assert all_playlist.count()  > 1
    logger.debug(f"all_playlist.count() = {all_playlist.count()}")
    p.delete_instance()


def test_video():
    v = VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    assert v.title == "test"
    try:
        VideoModel.create(title="test")

    except peewee.IntegrityError:
        assert len(VideoModel.select()) == 1

    v3, created3 = VideoModel.get_or_create(title="test")
    assert v3.title == "test"
    assert created3 is False
    assert len(VideoModel.select()) == 1
    v.my_delete_instance()


def test_delete_series():
    s = Series.create(name="test")
    assert s is not None
    s.my_delete_instance()
    s2 = Series.get_or_none(Series.name == "test")
    assert s2 is None


def test_create_channel_file(test_files):
    target = Path(config["paths"]["working"]) / "test_file_output"

    c = Channel.create(name="test", url="www.yahoo.com", youtube_id="asbsdrjgkdlsa;")

    assert c is not None

    for file in test_files:
        # with open(source / file, "rb") as src_file:
        #     f: FileInfo = {"name": file, "size": 100, "data": src_file.read()}

        new_name = target / file
        file_type = get_file_type(file)
        nf1 = File(
            path=new_name.parent,
            filename=new_name,
            file_type=file_type,
            extension="asdf",
            channel=c,
        )
        assert nf1 is not None
        assert nf1.extension == "asdf"

        nf2 = File.get_or_create(
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
    c.my_delete_instance()
