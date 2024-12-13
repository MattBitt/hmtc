import pytest

from hmtc.domains.user import User
from hmtc.models import Section as SectionModel
from hmtc.models import User as UserModel
from hmtc.repos.base_repo import Repository

testing_user_dict = {
    "id": 101,
    "username": "testuser",
    "email": "asdf@jkqwer.com",
    "hashed_password": "1234",
    "jellyfin_id": "1234",
}


def test_empty_user():
    c = User()
    assert type(c.repo) == Repository


def test_user_create_and_load(seeded_db):
    created_user = User.create(testing_user_dict)
    assert created_user.username == testing_user_dict["username"]
    assert created_user.email == testing_user_dict["email"]
    assert created_user.hashed_password == testing_user_dict["hashed_password"]
    assert created_user.jellyfin_id == testing_user_dict["jellyfin_id"]
    assert created_user.id > 0

    loaded_user = User.load(created_user.id)
    assert loaded_user.username == testing_user_dict["username"]
    assert loaded_user.email == testing_user_dict["email"]
    assert loaded_user.hashed_password == testing_user_dict["hashed_password"]
    assert loaded_user.jellyfin_id == testing_user_dict["jellyfin_id"]

    User.delete_id(created_user.id)


def test_user_delete(seeded_db):
    new_user = User.create(testing_user_dict)
    User.delete_id(new_user.id)


def test_serialize(seeded_db):
    _user = UserModel.select().first()
    user = User.serialize(_user.id)
    assert user["id"] == _user.id
    assert user["username"] == _user.username
    assert user["email"] == _user.email
    assert user["hashed_password"] == _user.hashed_password
    assert user["jellyfin_id"] == _user.jellyfin_id


def test_get_all(seeded_db):
    all_users = User.get_all()
    assert len(list(all_users)) == 3


def test_update_users(seeded_db):
    USER_ID = 1
    user = User.load(USER_ID)
    orig_name = user.username
    assert user.username == "john_doe"
    User.update({"username": "A whole nother name", "id": 1})
    assert UserModel.get_by_id(USER_ID).username == "A whole nother name"
    User.update({"username": orig_name, "id": USER_ID})
    assert UserModel.get_by_id(USER_ID).username == orig_name
