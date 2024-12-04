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


def test_series():
    s, created = Series.get_or_create(
        name="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created == True
    assert s.name == "test"

    all_series = Series.select()
    assert all_series.count() == 1
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

    p.delete_instance()


def test_video():
    v = VideoModel.create(
        youtube_id="abcdefghijk",
        title="Test Youtube Video",
        upload_date="2020-01-01",
        episode="",
        duration=8531,
        description="this is a test",
    )
    assert v.title == "Test Youtube Video"
    try:
        VideoModel.create(title="Test Youtube Video")
    except peewee.IntegrityError:
        # fail on purpose
        assert len(VideoModel.select()) == 1

    v3, created3 = VideoModel.get_or_create(title="Test Youtube Video")
    assert v3.title == "Test Youtube Video"
    assert created3 is False
    assert len(VideoModel.select()) == 1
    v.delete_instance()
    assert len(VideoModel.select()) == 0


def test_delete_series():
    s = Series.create(name="test")
    assert s is not None
    s.delete_instance()
    s2 = Series.get_or_none(Series.name == "test")
    assert s2 is None
