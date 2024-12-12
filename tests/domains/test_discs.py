from hmtc.domains.disc import Disc
from hmtc.models import Disc as DiscModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    disc_dict1,
    disc_dict2,
    disc_dict3,
    disc_item,
)


def test_empty_disc():
    c = Disc()
    assert type(c.repo) == Repository


def test_disc_create_and_load(disc_dict1, album_item):
    created_disc = Disc().create(disc_dict1)
    assert created_disc.title == disc_dict1["title"]

    assert created_disc.id > 0
    loaded_disc = Disc().load(created_disc.id)
    assert loaded_disc.title == disc_dict1["title"]


def test_disc_delete(disc_item, album_item):
    Disc.delete_id(disc_item.id)
    c = DiscModel.select().where(DiscModel.id == disc_item.id).get_or_none()
    assert c is None


def test_serialize(disc_dict1, album_item):
    new_id = Disc.create(disc_dict1)
    s = Disc.serialize(new_id)
    assert s["title"] == disc_dict1["title"]


def test_get_all(disc_dict1, disc_dict2, disc_dict3, album_item):
    Disc.create(disc_dict1)
    Disc.create(disc_dict2)
    Disc.create(disc_dict3)
    all_discs = Disc.get_all()
    assert len(list(all_discs)) == 3


def test_update_discs(disc_dict1, album_item):
    new_id = Disc.create(disc_dict1)
    disc = Disc.load(new_id)
    assert disc.title == disc_dict1["title"]
    Disc.update({"title": "A whole nother title", "id": new_id})
    assert DiscModel.get_by_id(new_id).title == "A whole nother title"


def test_disc_item(disc_item, disc_dict1):
    assert disc_item.title == disc_dict1["title"]
