from pathlib import Path

import peewee
import pytest
from loguru import logger

from hmtc.config import init_config
from hmtc.models import (
    Channel,
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
    assert len(Section.select()) == 0


# this test leaves a record in the database
def test_permanance_setup():
    s = Series.create(title="testing permanent record")
    assert s is not None


def test_permanance_execute():
    s = Series.get_or_none(Series.title == "testing permanent record")
    assert s is None
