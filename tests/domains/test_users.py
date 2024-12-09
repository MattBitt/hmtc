import pytest

from hmtc.domains.user import User
from hmtc.models import Section as SectionModel
from hmtc.models import User as UserModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    user_dict1,
    user_dict2,
    user_dict3,
    user_item,
)


def test_empty_user():
    c = User()
    assert type(c.repo) == Repository


def test_user_create_and_load(user_dict1):
    created_user = User.create(user_dict1)
    assert created_user.username == user_dict1["username"]
    assert created_user.email == user_dict1["email"]
    assert created_user.hashed_password == user_dict1["hashed_password"]
    assert created_user.jellyfin_id == user_dict1["jellyfin_id"]
    assert created_user.id > 0

    loaded_user = User.load(created_user.id)
    assert loaded_user.username == user_dict1["username"]
    assert loaded_user.email == user_dict1["email"]
    assert loaded_user.hashed_password == user_dict1["hashed_password"]
    assert loaded_user.jellyfin_id == user_dict1["jellyfin_id"]


def test_user_delete(user_item):

    User.delete_id(user_item.id)
    t = UserModel.select().where(UserModel.id == user_item.id).get_or_none()
    assert t is None


def test_serialize(user_item):
    t = User.serialize(user_item.id)
    assert t["id"] == user_item.id
    assert t["username"] == user_item.username
    assert t["email"] == user_item.email
    assert t["hashed_password"] == user_item.hashed_password
    assert t["jellyfin_id"] == user_item.jellyfin_id


def test_get_all(user_item):
    all_users = User.get_all()
    assert len(list(all_users)) == 1


def test_update_users(user_item):
    user = User.load(user_item.id)
    assert user.username == user_item.username
    User.update({"username": "antidis", "id": user_item.id})
    assert UserModel.get_by_id(user_item.id).username == "antidis"
