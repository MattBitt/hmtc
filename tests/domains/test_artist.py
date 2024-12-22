import pytest
from hmtc.domains.artist import Artist
from hmtc.models import Artist as ArtistModel


def test_artist_create_and_load(artist_dicts):
    ad = artist_dicts[0]
    created_artist = Artist.create(ad)

    assert created_artist.instance.name == ad["name"]
    assert created_artist.instance.id > 0

    loaded_artist = Artist.load(created_artist.instance.id)
    assert loaded_artist.instance.name == ad["name"]
    created_artist.delete()


def test_artist_create_no_name(artist_dicts):
    ad = artist_dicts[0]
    del ad["name"]
    try:
        Artist.create(ad)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)


def test_get_by_id(artist_item):
    loaded_artist = Artist.get_by(id=artist_item.instance.id)
    assert loaded_artist.instance.name == artist_item.instance.name


def test_get_by_name(artist_item):
    loaded_artist = Artist.get_by(name=artist_item.instance.name)
    assert loaded_artist.instance.name == artist_item.instance.name


def test_select_where(artist_item):
    artist_query = Artist.select_where(name=artist_item.instance.name)
    assert len(artist_query) == 1
    artist = artist_query[0]
    assert artist.instance.name == artist_item.instance.name


def test_update_artist(artist_item):
    artist = artist_item
    new_artist = artist.update({"name": "Updated Name"})
    assert new_artist.instance.name == "Updated Name"

    artist_from_db = (
        ArtistModel.select().where(ArtistModel.id == artist.instance.id).get()
    )
    assert artist_from_db.name == "Updated Name"


def test_artist_delete(artist_item):
    artist = artist_item
    artist.delete()
    a = (
        ArtistModel.select()
        .where(ArtistModel.id == artist_item.instance.id)
        .get_or_none()
    )
    assert a is None


def test_serialize(artist_item):
    a = artist_item.serialize()
    assert a["name"] == artist_item.instance.name
