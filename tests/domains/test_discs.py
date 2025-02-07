import pytest

from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel


def test_disc_create_and_load(disc_dicts, album_dicts):
    # setup
    album = Album.create(album_dicts[0])
    dd = disc_dicts[0]
    dd["album_id"] = album.instance.id
    created_disc = Disc.create(dd)

    # test
    assert created_disc.instance.title == dd["title"]
    assert created_disc.instance.id > 0

    loaded_disc = Disc.load(created_disc.instance.id)
    assert loaded_disc.instance.title == dd["title"]
    # teardown
    created_disc.delete()
    album.delete()


def test_disc_create_no_title(disc_dicts):
    dd = disc_dicts[0]
    del dd["title"]
    try:
        Disc.create(dd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(disc_item):
    loaded_disc = Disc.get_by(id=disc_item.instance.id)
    assert loaded_disc.instance.title == disc_item.instance.title


def test_get_by_title(disc_item):
    loaded_disc = Disc.get_by(title=disc_item.instance.title)
    assert loaded_disc.instance.title == disc_item.instance.title


def test_select_where(disc_item):
    disc_query = Disc.select_where(title=disc_item.instance.title)
    assert len(disc_query) == 1
    disc = disc_query[0]
    assert disc.instance.title == disc_item.instance.title


def test_update_disc(disc_item):
    disc = disc_item
    new_disc = disc.update({"title": "New Title"})
    assert new_disc.instance.title == "New Title"

    disc_from_db = DiscModel.select().where(DiscModel.id == disc.instance.id).get()
    assert disc_from_db.title == "New Title"


def test_disc_delete(disc_item):
    disc = disc_item
    disc.delete()
    d = DiscModel.select().where(DiscModel.id == disc_item.instance.id).get_or_none()
    assert d is None


def test_serialize(disc_item):
    s = disc_item.serialize()
    assert s["title"] == disc_item.instance.title


def test_count(disc_dicts, album_item):

    dd1 = disc_dicts[0]
    dd1["album_id"] = album_item.instance.id
    dd2 = disc_dicts[1]
    dd2["album_id"] = album_item.instance.id
    dd3 = disc_dicts[2]
    dd3["album_id"] = album_item.instance.id

    assert Disc.count() == 0
    Disc.create(dd1)
    Disc.create(dd2)
    Disc.create(dd3)
    assert Disc.count() == 3

    for disc_dict in disc_dicts:
        disc = Disc.get_by(title=disc_dict["title"])
        disc.delete()

    assert Disc.count() == 0


def test_disc_video(disc_item, video_item):
    print(disc_item.instance.album)
    dv = DiscVideoModel.create(
        video_id=video_item.instance.id, disc_id=disc_item.instance.id, order=1
    )
    assert len(disc_item.instance.dv.select()) == 1

    print(dv)
