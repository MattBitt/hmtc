import pytest

from hmtc.domains.artist import Artist
from hmtc.models import Artist as ArtistModel
from hmtc.models import Section as SectionModel
from hmtc.repos.base_repo import Repository

testing_artist_dict = {
    "id": 204,
    "name": "Some Test Artist",
    "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
}


def test_empty_artist(empty_db):
    c = Artist()
    assert type(c.repo) == Repository


def test_artist_create_and_load(empty_db):
    created_artist = Artist.create(testing_artist_dict)
    assert created_artist.name == testing_artist_dict["name"]
    assert created_artist.url == testing_artist_dict["url"]
    assert created_artist.id > 0

    loaded_artist = Artist.load(created_artist.id)

    assert loaded_artist.name == testing_artist_dict["name"]
    assert loaded_artist.url == testing_artist_dict["url"]

    Artist.delete_id(created_artist.id)


def test_artist_delete(seeded_db):
    new_artist = Artist.create(testing_artist_dict)
    assert new_artist.id > 0
    Artist.delete_id(new_artist.id)
    t = ArtistModel.select().where(ArtistModel.id == new_artist.id).get_or_none()
    assert t is None


def test_serialize(seeded_db):
    art = Artist.create(testing_artist_dict)
    artist = Artist.serialize(art.id)
    assert artist["id"] == art.id
    assert artist["name"] == art.name
    assert artist["url"] == art.url
    Artist.delete_id(art.id)


def test_get_all(seeded_db):
    all_artists = Artist.get_all()
    assert len(list(all_artists)) == 2


def test_update_artists(seeded_db):
    ARTIST_ID = 1
    ARTIST_NAME = "Harry Mack"

    artist = Artist.load(ARTIST_ID)
    assert artist.name == ARTIST_NAME
    Artist.update({"name": "MizzleBizzle", "id": ARTIST_ID})
    assert ArtistModel.get_by_id(ARTIST_ID).name == "MizzleBizzle"
    Artist.update({"name": ARTIST_NAME, "id": ARTIST_ID})
