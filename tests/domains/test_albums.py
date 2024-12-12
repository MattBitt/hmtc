import pytest

from hmtc.domains.album import Album
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_dict1,
    album_dict2,
    album_dict3,
    album_item,
    channel_dict1,
    channel_dict2,
    channel_dict3,
    channel_item,
    series_item,
    video_dict1,
    video_dict2,
    video_dict3,
    video_item,
)


def test_empty_album():
    c = Album()
    assert type(c.repo) == Repository


def test_album_create_and_load(album_dict1):
    created_album = Album.create(album_dict1)
    assert created_album.title == album_dict1["title"]

    assert created_album.id > 0

    loaded_album = Album.load(created_album.id)
    assert loaded_album.title == album_dict1["title"]


def test_album_delete(album_item):

    Album.delete_id(album_item.id)
    c = AlbumModel.select().where(AlbumModel.id == album_item.id).get_or_none()
    assert c is None


def test_serialize(album_item):
    s = Album.serialize(album_item.id)
    assert s["title"] == album_item.title
    assert s["id"] == album_item.id


def test_get_all(album_item):
    all_albums = Album.get_all()
    assert len(list(all_albums)) == 1


def test_update_albums(album_item):
    album = Album.load(album_item.id)
    assert album.title == album_item.title
    Album.update({"title": "A whole nother title", "id": album_item.id})
    assert AlbumModel.get_by_id(album_item.id).title == "A whole nother title"


def test_add_video_to_album(album_item, video_item):
    Album.add_video(album_item.id, video_item.id)
    album = Album.load(album_item.id)
    vids = Album.get_videos(album.id)
    assert len(vids) == 1
    assert vids[0].id == video_item.id
