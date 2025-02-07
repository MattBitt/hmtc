import pytest

from hmtc.domains.album import Album
from hmtc.models import Album as AlbumModel


def test_album_create_and_load(album_dicts):
    ad = album_dicts[0]
    created_album = Album.create(ad)
    assert created_album.instance.title == ad["title"]
    assert created_album.instance.id > 0

    loaded_album = Album.load(created_album.instance.id)
    assert loaded_album.instance.title == ad["title"]
    created_album.delete()


def test_album_create_no_title(album_dicts):
    ad = album_dicts[0]
    del ad["title"]
    try:
        Album.create(ad)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(album_dicts):
    ad = album_dicts[1]
    created_album = Album.create(ad)
    loaded_album = Album.get_by(id=created_album.instance.id)
    assert loaded_album.instance.title == ad["title"]
    created_album.delete()


def test_get_by_title(album_dicts):
    ad = album_dicts[1]
    created_album = Album.create(ad)
    loaded_album = Album.get_by(title=created_album.instance.title)
    assert loaded_album.instance.title == ad["title"]
    created_album.delete()


def test_select_where(album_dicts):
    ad1 = album_dicts[1]
    ad2 = album_dicts[2]
    album1 = Album.create(ad1)
    album2 = Album.create(ad2)

    album_query = Album.select_where(title=album1.instance.title)
    assert len(album_query) == 1
    album_item = Album(album_query[0].instance.id)
    assert album_item.instance.title == ad1["title"]
    loaded_album = album_query[0]
    assert loaded_album.instance.title == ad1["title"]
    album1.delete()
    album2.delete()


def test_update_album(album_dicts):
    ad = album_dicts[2]
    album = Album.create(ad)
    new_album = album.update({"title": "New Title"})
    assert new_album.instance.title == "New Title"

    album_from_db = AlbumModel.select().where(AlbumModel.id == album.instance.id).get()
    assert album_from_db.title == "New Title"
    album.delete()


def test_album_delete(album_dicts):
    ad = album_dicts[1]
    created_album = Album.create(ad)
    created_album.delete()
    a = (
        AlbumModel.select()
        .where(AlbumModel.id == created_album.instance.id)
        .get_or_none()
    )
    assert a is None


def test_serialize(album_dicts):
    ad = album_dicts[2]
    album = Album.create(ad)
    s = album.serialize()
    assert s["title"] == ad["title"]
    album.delete()


def test_count(album_dicts):
    ad1 = album_dicts[0]
    ad2 = album_dicts[1]
    ad3 = album_dicts[2]

    assert Album.count() == 0
    Album.create(ad1)
    Album.create(ad2)
    Album.create(ad3)
    assert Album.count() == 3

    for album_dict in album_dicts:
        album = Album.get_by(title=album_dict["title"])
        album.delete()

    assert Album.count() == 0


def test_add_video(album_item, video_item):
    album = album_item
    album.add_video(video_item.instance)
    assert album.videos_count() == 1
    album.delete()
