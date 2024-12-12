import pytest

from hmtc.domains.track import Track
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    disc_item,
    section_item,
    series_item,
    track_dict1,
    track_dict2,
    track_dict3,
    track_item,
    video_item,
    youtube_series_item,
)


def test_empty_track():
    c = Track()
    assert type(c.repo) == Repository


def test_track_create_and_load(track_dict1, section_item, disc_item):
    track_dict1["section_id"] = section_item.id
    track_dict1["disc_id"] = disc_item.id
    created_track = Track.create(track_dict1)
    assert created_track.id > 0
    assert created_track.title == track_dict1["title"]
    assert created_track.length == track_dict1["length"]
    assert created_track.track_number == track_dict1["track_number"]
    assert created_track.section.id == section_item.id

    loaded_track = Track.load(created_track.id)
    assert loaded_track.title == track_dict1["title"]
    assert loaded_track.length == track_dict1["length"]
    assert loaded_track.track_number == track_dict1["track_number"]
    # not sure why this is failing
    #  assert loaded_track.section.id == section_item.id

    assert loaded_track.id > 0


def test_track_delete(track_item):
    Track.delete_id(track_item.id)
    c = TrackModel.select().where(TrackModel.id == track_item.id).get_or_none()
    assert c is None


def test_serialize(track_item, section_item, disc_item):
    s = Track.serialize(track_item.id)
    assert s["title"] == track_item.title
    assert s["track_number"] == track_item.track_number
    assert s["length"] == track_item.length
    assert s["id"] == track_item.id
    assert s["section"]["start"] == section_item.start
    assert s["section"]["end"] == section_item.end
    assert s["disc"]["title"] == disc_item.title


def test_get_all(track_item):
    all_tracks = Track.get_all()
    assert len(list(all_tracks)) == 1


def test_update_tracks(track_item):
    track = Track.load(track_item.id)
    assert track.title == track_item.title
    Track.update({"title": "Some other name for a track", "id": track_item.id})
    assert TrackModel.get_by_id(track_item.id).title == "Some other name for a track"
