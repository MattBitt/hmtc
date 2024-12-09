import pytest

from hmtc.domains.artist import Artist
from hmtc.models import Section as SectionModel
from hmtc.models import Artist as ArtistModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    artist_dict1,
    artist_dict2,
    artist_dict3,
    artist_item,
)


def test_empty_artist():
    c = Artist()
    assert type(c.repo) == Repository


def test_artist_create_and_load(artist_dict1):
    created_artist = Artist.create(artist_dict1)
    assert created_artist.name == artist_dict1["name"]
    assert created_artist.url == artist_dict1["url"]
    assert created_artist.id > 0

    loaded_artist = Artist.load(created_artist.id)
    assert loaded_artist.name == artist_dict1["name"]
    assert loaded_artist.url == artist_dict1["url"]


def test_artist_delete(artist_item):

    Artist.delete_id(artist_item.id)
    t = ArtistModel.select().where(ArtistModel.id == artist_item.id).get_or_none()
    assert t is None


def test_serialize(artist_item):
    t = Artist.serialize(artist_item.id)
    assert t["id"] == artist_item.id
    assert t["name"] == artist_item.name
    assert t["url"] == artist_item.url


def test_get_all(artist_item):
    all_artists = Artist.get_all()
    assert len(list(all_artists)) == 1


def test_update_artists(artist_item):
    artist = Artist.load(artist_item.id)
    assert artist.name == artist_item.name
    Artist.update({"name": "antidis", "id": artist_item.id})
    assert ArtistModel.get_by_id(artist_item.id).name == "antidis"
