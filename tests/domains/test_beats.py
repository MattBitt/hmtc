import pytest

from hmtc.domains.beat import Beat
from hmtc.models import Beat as BeatModel
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository

testing_beat_dict = {
    "id": 807,
    "title": "Some Test Beat Title",
}


def test_empty_beat(empty_db):
    c = Beat()
    assert type(c.repo) == Repository


def test_beat_create_and_load(empty_db):
    created_beat = Beat.create(testing_beat_dict)
    assert created_beat.title == testing_beat_dict["title"]
    assert created_beat.id > 0

    loaded_beat = Beat.load(created_beat.id)
    assert loaded_beat.title == testing_beat_dict["title"]
    assert loaded_beat.id == created_beat.id

    Beat.delete_id(created_beat.id)


def test_beat_delete(seeded_db):
    new_beat = Beat.create(testing_beat_dict)
    Beat.delete_id(new_beat.id)
    t = BeatModel.select().where(BeatModel.id == new_beat.id).get_or_none()
    assert t is None


def test_serialize(seeded_db):
    _beat = Beat.create(testing_beat_dict)
    beat = Beat.serialize(_beat.id)
    assert beat["id"] == _beat.id
    assert beat["title"] == _beat.title
    Beat.delete_id(_beat.id)


def test_get_all(seeded_db):
    all_beats = Beat.get_all()
    assert len(list(all_beats)) == 0


def test_update_beats(seeded_db):
    beat = Beat.create(testing_beat_dict)

    orig_title = beat.title

    Beat.update({"title": "A whole nother title", "id": beat.id})
    assert BeatModel.get_by_id(beat.id).title == "A whole nother title"
    Beat.update({"title": orig_title, "id": beat.id})
    assert BeatModel.get_by_id(beat).title == orig_title
