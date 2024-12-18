import pytest
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.section import Section
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.domains.track import Track
from hmtc.models import Disc as DiscModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.repos.base_repo import Repository

testing_track_dict = {
    "title": "Random Track Title",
    "length": 1000,
    "track_number": 1,
    "track_number_verbose": "001",
}

testing_section_dict = {
    "start": 0,
    "end": 100,
    "section_type": "verse",
}

testing_video_dict = {
    "title": "Orange Frisbee Jello",
    "description": "Some Test Video Description",
    "url": "https://www.youtube.com/watch?v=123456",
    "youtube_id": "acedgiedsae",
    "duration": 100,
    "upload_date": "2021-01-01",
}

testing_channel_dict = {
    "title": "Marmalade Channel",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "hkjfaesdl",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


testing_album_dict = {
    "title": "Cool Sounding Album",
    "release_date": "2021-01-01",
}

testing_disc_dict = {
    "title": "Another Random Disc in Testing",
}


def test_empty_track():
    c = Track()
    assert type(c.repo) == Repository


def test_track_create_and_load(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)

    album = Album.create(testing_album_dict)
    testing_disc_dict["_album"] = album.my_dict()
    disc = Disc.create(testing_disc_dict)
    assert disc.title == testing_disc_dict["title"]

    testing_track_dict["section"] = section.my_dict()
    testing_track_dict["disc"] = disc.my_dict()

    created_track = Track.create(testing_track_dict)
    assert created_track.id > 0
    assert created_track.title == testing_track_dict["title"]
    assert created_track.length == testing_track_dict["length"]
    assert created_track.track_number == testing_track_dict["track_number"]
    assert created_track.section.id == section.id
    assert created_track.disc.id == disc.id
    assert created_track.section.id == section.id
    assert created_track.section.video.id == video.id
    assert created_track.disc.album.id == album.id
    loaded_track = Track.load(created_track.id)
    assert loaded_track.title == testing_track_dict["title"]
    assert loaded_track.length == testing_track_dict["length"]
    assert loaded_track.track_number == testing_track_dict["track_number"]

    assert loaded_track.id > 0
    assert loaded_track.section.id == section.id
    assert loaded_track.disc.id == disc.id

    Track.delete_id(created_track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_track_delete(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)

    album = Album.create(testing_album_dict)
    testing_disc_dict["_album"] = album.my_dict()
    disc = Disc.create(testing_disc_dict)
    assert disc.title == testing_disc_dict["title"]

    testing_track_dict["section"] = section.my_dict()
    testing_track_dict["disc"] = disc.my_dict()

    new_track = Track.create(testing_track_dict)

    Track.delete_id(new_track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)

    album = Album.create(testing_album_dict)
    testing_disc_dict["_album"] = album.my_dict()
    disc = Disc.create(testing_disc_dict)
    assert disc.title == testing_disc_dict["title"]

    testing_track_dict["section"] = section.my_dict()
    testing_track_dict["disc"] = disc.my_dict()

    _track = Track.create(testing_track_dict)
    track = Track.serialize(_track.id)
    assert track["title"] == _track.title
    assert track["track_number"] == _track.track_number
    assert track["length"] == _track.length
    assert track["id"] == _track.id
    assert track["section"]["start"] == _track.section.start
    assert track["section"]["end"] == _track.section.end
    assert track["disc"]["title"] == _track.disc.title
    assert track["disc"]["album"]["title"] == _track.disc.album.title
    Track.delete_id(_track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_get_all(seeded_db):
    all_tracks = Track.get_all()
    assert len(list(all_tracks)) == 0


def test_update_tracks(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_section_dict["_video"] = video.my_dict()
    section = Section.create(testing_section_dict)

    album = Album.create(testing_album_dict)
    testing_disc_dict["_album"] = album.my_dict()
    disc = Disc.create(testing_disc_dict)
    assert disc.title == testing_disc_dict["title"]

    testing_track_dict["section"] = section.my_dict()
    testing_track_dict["disc"] = disc.my_dict()

    track = Track.create(testing_track_dict)
    orig_title = track.title
    assert track.title == "Random Track Title"
    Track.update({"title": "A whole nother title", "id": track.id})
    assert TrackModel.get_by_id(track.id).title == "A whole nother title"
    Track.update({"title": orig_title, "id": track.id})
    assert TrackModel.get_by_id(track.id).title == orig_title

    Track.delete_id(track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)
