import pytest

from hmtc.domains.album import Album
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.repos.base_repo import Repository

testing_video_dict = {
    "id": 101,
    "description": "This is only for testing. If you see this on the website, something is wrong.",
    "duration": 400,
    "title": "Some Test Titile that i just made up",
    "unique_content": True,
    "upload_date": "2021-01-01",
    "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
    "youtube_id": "1234adfaewr",
    "episode": 1,
    "channel_id": "1",
}

testing_album_dict = {
    "id": 102,
    "title": "Some Test Album Title",
    "release_date": "2021-01-01",
}


def test_empty_album(empty_db):
    c = Album()
    assert type(c.repo) == Repository


def test_album_create_and_load(empty_db):
    created_album = Album.create(testing_album_dict)
    assert created_album.title == testing_album_dict["title"]
    assert created_album.id > 0

    loaded_album = Album.load(created_album.id)
    assert loaded_album.title == testing_album_dict["title"]

    Album.delete_id(created_album.id)


def test_album_delete(seeded_db):
    new_album = Album.create(testing_album_dict)
    assert new_album.id > 0
    Album.delete_id(new_album.id)


def test_serialize(seeded_db):
    _album = AlbumModel.select().first()
    album = Album.serialize(_album.id)
    assert album["title"] == _album.title
    assert album["id"] == _album.id


def test_get_all(seeded_db):
    all_albums = Album.get_all()
    assert len(list(all_albums)) == 3


def test_update_albums(seeded_db):
    ALBUM_ID = 1
    album = Album.load(ALBUM_ID)
    orig_title = album.title
    assert album.title == "Omegle Bars"
    Album.update({"title": "A whole nother title", "id": 1})
    assert AlbumModel.get_by_id(ALBUM_ID).title == "A whole nother title"
    Album.update({"title": orig_title, "id": ALBUM_ID})
    assert AlbumModel.get_by_id(ALBUM_ID).title == orig_title


def test_add_video_to_album(seeded_db):
    new_vid = Video.create(testing_video_dict)
    Album.add_video(1, new_vid.id, 1)
    album = Album.load(1)
    vids = Album.get_videos(album.id)
    assert len(vids) == 5
    assert new_vid.id in [vid.id for vid in vids]
    # need to clean up
    Video.delete_id(new_vid.id)
