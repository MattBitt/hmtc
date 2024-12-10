import pytest

from hmtc.domains.beat import Beat
from hmtc.models import Beat as BeatModel
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    beat_dict1,
    beat_dict2,
    beat_dict3,
    beat_item,
)


def test_empty_beat():
    c = Beat()
    assert type(c.repo) == Repository


def test_beat_create_and_load(beat_dict1):
    created_beat = Beat.create(beat_dict1)
    assert created_beat.title == beat_dict1["title"]
    assert created_beat.id > 0

    loaded_beat = Beat.load(created_beat.id)
    assert loaded_beat.title == beat_dict1["title"]
    assert loaded_beat.id == created_beat.id


def test_beat_delete(beat_item):

    Beat.delete_id(beat_item.id)
    t = BeatModel.select().where(BeatModel.id == beat_item.id).get_or_none()
    assert t is None


def test_serialize(beat_item):
    t = Beat.serialize(beat_item.id)
    assert t["id"] == beat_item.id
    assert t["title"] == beat_item.title


def test_get_all(beat_item):
    all_beats = Beat.get_all()
    assert len(list(all_beats)) == 1


def test_update_beats(beat_item):
    beat = Beat.load(beat_item.id)
    assert beat.title == beat_item.title
    Beat.update({"title": "antidis", "id": beat_item.id})
    assert BeatModel.get_by_id(beat_item.id).title == "antidis"
