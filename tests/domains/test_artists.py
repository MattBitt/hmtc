import pytest

from hmtc.domains.artist import Artist
from hmtc.models import Artist as ArtistModel
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository


def test_empty_artist(empty_db):
    c = Artist()
    assert type(c.repo) == Repository


def test_artist_create_and_load(empty_db, artist_dict):
    created_artist = Artist.create(artist_dict)
    assert created_artist.name == artist_dict["name"]
    assert created_artist.url == artist_dict["url"]
    assert created_artist.id > 0

    loaded_artist = Artist.load(created_artist.id)

    assert loaded_artist.name == artist_dict["name"]
    assert loaded_artist.url == artist_dict["url"]

    Artist.delete_id(created_artist.id)


def test_artist_delete(seeded_db, artist_dict):
    new_artist = Artist.create(artist_dict)
    assert new_artist.id > 0
    Artist.delete_id(new_artist.id)
    t = ArtistModel.select().where(ArtistModel.id == new_artist.id).get_or_none()
    assert t is None


def test_serialize(seeded_db, artist_dict):
    art = Artist.create(artist_dict)
    artist = Artist.serialize(art.id)
    assert artist["id"] == art.id
    assert artist["name"] == art.name
    assert artist["url"] == art.url
    Artist.delete_id(art.id)


def test_get_all(seeded_db):
    all_artists = Artist.get_all()
    assert len(list(all_artists)) == 2


def test_update_artists(seeded_db, artist_dict):
    artist = Artist.create(artist_dict)

    assert artist.name == "Some Test Artist"
    Artist.update({"name": "MizzleBizzle", "id": artist.id})
    assert ArtistModel.get_by_id(artist.id).name == "MizzleBizzle"
    Artist.update({"name": "Some Test Artist", "id": artist.id})
