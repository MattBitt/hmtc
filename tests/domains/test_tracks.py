import pytest

from hmtc.domains.track import Track
from hmtc.models import Disc as DiscModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository

testing_track_dict = {
    "id": 807,
    "title": "Some Test Track Title",
    "length": 1000,
    "track_number": 1,
    "track_number_verbose": "001",
}


def test_empty_track():
    c = Track()
    assert type(c.repo) == Repository


def test_track_create_and_load(seeded_db):
    section = SectionModel.select().first()
    testing_track_dict["section_id"] = section.id

    disc = DiscModel.select().first()
    testing_track_dict["disc_id"] = disc.id

    created_track = Track.create(testing_track_dict)
    assert created_track.id > 0
    assert created_track.title == testing_track_dict["title"]
    assert created_track.length == testing_track_dict["length"]
    assert created_track.track_number == testing_track_dict["track_number"]
    assert created_track.section.id == section.id
    assert created_track.disc.id == disc.id

    loaded_track = Track.load(created_track.id)
    assert loaded_track.title == testing_track_dict["title"]
    assert loaded_track.length == testing_track_dict["length"]
    assert loaded_track.track_number == testing_track_dict["track_number"]

    assert loaded_track.id > 0
    assert loaded_track.section.id == section.id
    assert loaded_track.disc.id == disc.id

    Track.delete_id(created_track.id)


def test_track_delete(seeded_db):
    section = SectionModel.select().first()
    testing_track_dict["section_id"] = section.id

    disc = DiscModel.select().first()
    testing_track_dict["disc_id"] = disc.id

    new_track = Track.create(testing_track_dict)
    Track.delete_id(new_track.id)


def test_serialize(seeded_db):
    _track = TrackModel.select().first()
    track = Track.serialize(_track.id)
    assert track["title"] == _track.title
    assert track["track_number"] == _track.track_number
    assert track["length"] == _track.length
    assert track["id"] == _track.id
    assert track["section"]["start"] == _track.section.start
    assert track["section"]["end"] == _track.section.end
    assert track["disc"]["title"] == _track.disc.title


def test_get_all(seeded_db):
    all_tracks = Track.get_all()
    assert len(list(all_tracks)) == 3


def test_update_tracks(seeded_db):
    TRACK_ID = 1
    track = Track.load(TRACK_ID)
    orig_title = track.title
    assert track.title == "Track One"
    Track.update({"title": "A whole nother title", "id": 1})
    assert TrackModel.get_by_id(TRACK_ID).title == "A whole nother title"
    Track.update({"title": orig_title, "id": TRACK_ID})
    assert TrackModel.get_by_id(TRACK_ID).title == orig_title
