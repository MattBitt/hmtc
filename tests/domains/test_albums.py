import pytest

from hmtc.domains.album import Album
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.repos.base_repo import Repository

testing_video_dict = {
    "description": "This is only for testing. If you see this on the website, something is wrong.",
    "duration": 400,
    "title": "Some Test Titile that i just made up",
    "unique_content": True,
    "upload_date": "2021-01-01",
    "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
    "youtube_id": "inalbumstesting1234adfaewr",
    "episode": 1,
    "channel": {"title": "Harry Mack"},
}

testing_album_dict = {
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
    ALBUM_TITLE = "Omegle Bars"
    album = Album.repo.get_by(title=ALBUM_TITLE)
    album_id = album.id
    orig_title = album.title
    assert album.title == ALBUM_TITLE
    Album.update({"title": "A whole nother title", "id": album_id})
    assert AlbumModel.get_by_id(album_id).title == "A whole nother title"
    Album.update({"title": orig_title, "id": album_id})
    assert AlbumModel.get_by_id(album_id).title == orig_title
