import pytest
from hmtc.domains.track import Track
from hmtc.models import Track as TrackModel
from hmtc.domains.disc import Disc


def test_track_create_and_load(track_dicts, disc_item, section_item):
    # setup
    td = track_dicts[0]
    td["disc_id"] = disc_item.instance.id
    td["section_id"] = section_item.instance.id

    created_track = Track.create(td)

    # test
    assert created_track.instance.title == td["title"]
    assert created_track.instance.id > 0

    loaded_track = Track.load(created_track.instance.id)
    assert loaded_track.instance.title == td["title"]
    # teardown
    created_track.delete()


def test_track_create_no_title(track_dicts):
    td = track_dicts[0]
    del td["title"]
    try:
        Track.create(td)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(track_item):
    loaded_track = Track.get_by(id=track_item.instance.id)
    assert loaded_track.instance.title == track_item.instance.title


def test_get_by_title(track_item):
    loaded_track = Track.get_by(title=track_item.instance.title)
    assert loaded_track.instance.title == track_item.instance.title


def test_select_where(track_item):
    track_query = Track.select_where(title=track_item.instance.title)
    assert len(track_query) == 1
    track = track_query[0]
    assert track.instance.title == track_item.instance.title


def test_update_track(track_item):
    track = track_item
    new_track = track.update({"title": "New Title"})
    assert new_track.instance.title == "New Title"

    track_from_db = TrackModel.select().where(TrackModel.id == track.instance.id).get()
    assert track_from_db.title == "New Title"


def test_track_delete(track_item):
    track = track_item
    track.delete()
    t = TrackModel.select().where(TrackModel.id == track_item.instance.id).get_or_none()
    assert t is None


def test_serialize(track_item):
    s = track_item.serialize()
    assert s["title"] == track_item.instance.title


@pytest.mark.skip(f"Have to create individual sections for each track")
def test_count(track_dicts, disc_item):
    td1 = track_dicts[0]
    td1["disc_id"] = disc_item.instance.id
    td2 = track_dicts[1]
    td2["disc_id"] = disc_item.instance.id
    td3 = track_dicts[2]
    td3["disc_id"] = disc_item.instance.id

    assert Track.count() == 0
    Track.create(td1)
    Track.create(td2)
    Track.create(td3)
    assert Track.count() == 3

    for track_dict in track_dicts:
        track = Track.get_by(title=track_dict["title"])
        track.delete()

    assert Track.count() == 0
