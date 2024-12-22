import pytest

from hmtc.domains.beat import Beat
from hmtc.models import Beat as BeatModel


def test_beat_create_and_load(beat_dicts):
    bd = beat_dicts[0]
    created_beat = Beat.create(bd)

    assert created_beat.instance.title == bd["title"]
    assert created_beat.instance.id > 0

    loaded_beat = Beat.load(created_beat.instance.id)
    assert loaded_beat.instance.title == bd["title"]
    created_beat.delete()


def test_beat_create_no_title(beat_dicts):
    bd = beat_dicts[0]
    del bd["title"]
    try:
        Beat.create(bd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)


def test_get_by_id(beat_item):
    loaded_beat = Beat.get_by(id=beat_item.instance.id)
    assert loaded_beat.instance.title == beat_item.instance.title


def test_get_by_title(beat_item):
    loaded_beat = Beat.get_by(title=beat_item.instance.title)
    assert loaded_beat.instance.title == beat_item.instance.title


def test_select_where(beat_item):
    beat_query = Beat.select_where(title=beat_item.instance.title)
    assert len(beat_query) == 1
    beat = beat_query[0]
    assert beat.instance.title == beat_item.instance.title


def test_update_beat(beat_item):
    beat = beat_item
    new_beat = beat.update({"title": "Updated Title"})
    assert new_beat.instance.title == "Updated Title"

    beat_from_db = BeatModel.select().where(BeatModel.id == beat.instance.id).get()
    assert beat_from_db.title == "Updated Title"


def test_beat_delete(beat_item):
    beat = beat_item
    beat.delete()
    b = BeatModel.select().where(BeatModel.id == beat_item.instance.id).get_or_none()
    assert b is None


def test_serialize(beat_item):
    b = beat_item.serialize()
    assert b["title"] == beat_item.instance.title
