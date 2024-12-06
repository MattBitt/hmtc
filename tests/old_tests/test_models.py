from pathlib import Path

import peewee
import pytest
from loguru import logger

from hmtc.config import init_config
from hmtc.models import (
    Channel,
    File,
    Section,
    Series,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Video as VideoModel,
)

config = init_config()


def test_empty_db():
    assert len(Channel.select()) == 0
    assert len(Series.select()) == 0
    assert len(VideoModel.select()) == 0
    assert len(File.select()) == 0
    assert len(Section.select()) == 0


def test_series():
    s, created = Series.get_or_create(
        title="test", start_date="2020-01-01", end_date="2020-12-31"
    )
    assert created == True
    assert s.title == "test"

    all_series = Series.select()
    assert all_series.count() == 1
    s.delete_instance()


# this test leaves a record in the database
def test_permanance_setup():
    s = Series.create(title="testing permanent record")
    assert s is not None


def test_permanance_execute():
    s = Series.get_or_none(Series.title == "testing permanent record")
    assert s is None


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
    s = Series.create(title="test")
    assert s is not None
    s.delete_instance()
    s2 = Series.get_or_none(Series.title == "test")
    assert s2 is None
