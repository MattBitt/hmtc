import pytest

from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.disc import Disc
from hmtc.domains.section import Section
from hmtc.domains.track import Track
from hmtc.domains.video import Video
from hmtc.models import Disc as DiscModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository


def test_empty_track():
    c = Track()
    assert type(c.repo) == Repository


def test_track_create_and_load(
    seeded_db, video_dict, album_dict, section_dict, disc_dict, channel_dict, track_dict
):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()
    video = Video.create(video_dict)
    section_dict["_video"] = video.my_dict()
    section = Section.create(section_dict)
    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    disc = Disc.create(disc_dict)
    assert disc.title == disc_dict["title"]

    track_dict["section"] = section.my_dict()
    track_dict["disc"] = disc.my_dict()

    created_track = Track.create(track_dict)
    assert created_track.id > 0
    assert created_track.title == track_dict["title"]
    assert created_track.length == track_dict["length"]
    assert created_track.track_number == track_dict["track_number"]
    assert created_track.section.id == section.id
    assert created_track.disc.id == disc.id
    assert created_track.section.id == section.id
    assert created_track.section.video.id == video.id
    assert created_track.disc.album.id == album.id
    loaded_track = Track.load(created_track.id)
    assert loaded_track.title == track_dict["title"]
    assert loaded_track.length == track_dict["length"]
    assert loaded_track.track_number == track_dict["track_number"]

    assert loaded_track.id > 0
    assert loaded_track.section.id == section.id
    assert loaded_track.disc.id == disc.id

    Track.delete_id(created_track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_track_delete(seeded_db, track_item):

    Track.delete_id(track_item.id)


def test_serialize(seeded_db, track_item):
    track = Track.serialize(track_item.id)
    assert track["title"] == track_item.title
    assert track["track_number"] == track_item.track_number
    assert track["length"] == track_item.length
    assert track["id"] == track_item.id
    assert track["section"]["start"] == track_item.section.start
    assert track["section"]["end"] == track_item.section.end
    assert track["disc"]["title"] == track_item.disc.title
    assert track["disc"]["album"]["title"] == track_item.disc.album.title
    Track.delete_id(track_item.id)


def test_get_all(seeded_db):
    all_tracks = Track.get_all()
    assert len(list(all_tracks)) == 0


def test_update_tracks(seeded_db, track_item):
    orig_title = track_item.title
    assert track_item.title == "Random Track Title"
    Track.update({"title": "A whole nother title", "id": track_item.id})
    assert TrackModel.get_by_id(track_item.id).title == "A whole nother title"
    Track.update({"title": orig_title, "id": track_item.id})
    assert TrackModel.get_by_id(track_item.id).title == orig_title

    Track.delete_id(track_item.id)
