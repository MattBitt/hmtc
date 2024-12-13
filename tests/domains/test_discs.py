from hmtc.domains.disc import Disc
from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.repos.base_repo import Repository

testing_disc_dict = {
    "id": 101,
    "title": "Some Test Disc Title",
}


def test_empty_disc():
    c = Disc()
    assert type(c.repo) == Repository


def test_disc_create_and_load(seeded_db):
    album = AlbumModel.select().first()
    testing_disc_dict["album_id"] = album.id
    created_disc = Disc.create(testing_disc_dict)
    assert created_disc.title == testing_disc_dict["title"]

    assert created_disc.id > 0
    loaded_disc = Disc.load(created_disc.id)
    assert loaded_disc.title == testing_disc_dict["title"]
    assert loaded_disc.album.title == album.title
    Disc.delete_id(created_disc.id)


def test_disc_delete(seeded_db):
    album = AlbumModel.select().first()
    testing_disc_dict["album_id"] = album.id
    new_disc = Disc.create(testing_disc_dict)
    Disc.delete_id(new_disc.id)
    c = DiscModel.select().where(DiscModel.id == new_disc.id).get_or_none()
    assert c is None


def test_serialize(seeded_db):
    _disc = DiscModel.select().first()

    disc = Disc.serialize(_disc)
    assert disc["title"] == _disc.title


def test_get_all(seeded_db):
    all_discs = Disc.get_all()
    assert len(list(all_discs)) == 7


def test_update_discs(seeded_db):
    album = AlbumModel.select().first()
    testing_disc_dict["album_id"] = album.id
    new_disc = Disc.create(testing_disc_dict)
    disc = Disc.load(new_disc.id)
    assert disc.title == testing_disc_dict["title"]
    Disc.update({"title": "A whole nother title", "id": new_disc.id})
    assert DiscModel.get_by_id(new_disc.id).title == "A whole nother title"
