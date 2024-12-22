import pytest
from hmtc.domains.user import User
from hmtc.models import User as UserModel


def test_user_create_and_load(user_dicts):
    ud = user_dicts[0]
    created_user = User.create(ud)

    assert created_user.instance.username == ud["username"]
    assert created_user.instance.id > 0

    loaded_user = User.load(created_user.instance.id)
    assert loaded_user.instance.username == ud["username"]
    created_user.delete()


def test_user_create_no_username(user_dicts):
    ud = user_dicts[0]
    del ud["username"]
    try:
        User.create(ud)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)


def test_get_by_id(user_item):
    loaded_user = User.get_by(id=user_item.instance.id)
    assert loaded_user.instance.username == user_item.instance.username


def test_get_by_username(user_item):
    loaded_user = User.get_by(username=user_item.instance.username)
    assert loaded_user.instance.username == user_item.instance.username


def test_select_where(user_item):
    user_query = User.select_where(username=user_item.instance.username)
    assert len(user_query) == 1
    user = user_query[0]
    assert user.instance.username == user_item.instance.username


def test_update_user(user_item):
    user = user_item
    new_user = user.update({"username": "UpdatedUsername"})
    assert new_user.instance.username == "UpdatedUsername"

    user_from_db = UserModel.select().where(UserModel.id == user.instance.id).get()
    assert user_from_db.username == "UpdatedUsername"


def test_user_delete(user_item):
    user = user_item
    user.delete()
    u = UserModel.select().where(UserModel.id == user_item.instance.id).get_or_none()
    assert u is None


def test_serialize(user_item):
    u = user_item.serialize()
    assert u["username"] == user_item.instance.username
