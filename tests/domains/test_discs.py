from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.models import Album as AlbumModel
from hmtc.models import Disc as DiscModel
from hmtc.repos.base_repo import Repository


def test_empty_disc():
    c = Disc()
    assert type(c.repo) == Repository


def test_disc_create_and_load(seeded_db, album_dict, disc_dict):
    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    created_disc = Disc.create(disc_dict)
    assert created_disc.title == disc_dict["title"]

    assert created_disc.id > 0
    loaded_disc = Disc.load(created_disc.id)
    assert loaded_disc.title == disc_dict["title"]
    assert loaded_disc.album.title == album.title
    Disc.delete_id(created_disc.id)
    Album.delete_id(album.id)


def test_disc_delete(seeded_db, album_dict, disc_dict):
    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    new_disc = Disc.create(disc_dict)
    Disc.delete_id(new_disc.id)
    c = DiscModel.select().where(DiscModel.id == new_disc.id).get_or_none()
    assert c is None
    Disc.delete_id(new_disc.id)
    Album.delete_id(album.id)


def test_serialize(seeded_db, album_dict, disc_dict):
    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    new_disc = Disc.create(disc_dict)

    disc = Disc.serialize(new_disc)
    assert disc["title"] == new_disc.title
    Disc.delete_id(new_disc.id)
    Album.delete_id(album.id)


def test_get_all(seeded_db):
    all_discs = Disc.get_all()
    assert len(list(all_discs)) == 0


def test_update_discs(seeded_db, album_dict, disc_dict):
    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    disc = Disc.create(disc_dict)
    assert disc.title == disc_dict["title"]
    Disc.update({"title": "A whole nother title", "id": disc.id})
    assert DiscModel.get_by_id(disc.id).title == "A whole nother title"
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
