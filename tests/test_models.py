import pytest
from hmtc.models import (
    Video,
    Series,
    Channel,
    Playlist,
    Track,
)


def test_series():
    Series.create_table()
    s = Series.create(name="test")
    assert s.name == "test"
    s.delete_instance()


def test_permanance():
    s = Series.get_or_none(Series.name == "test")
    assert s is None
