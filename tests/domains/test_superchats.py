import pytest

from hmtc.domains.superchat import Superchat
from hmtc.models import Superchat as SuperchatModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    series_item,
    superchat_dict1,
    superchat_dict2,
    superchat_dict3,
    superchat_item,
    video_item,
    youtube_series_item,
)


def test_empty_superchat():
    c = Superchat()
    assert type(c.repo) == Repository


def test_superchat_create_and_load(superchat_dict1, video_item):
    superchat_dict1["video_id"] = video_item.id
    created_superchat = Superchat.create(superchat_dict1)
    assert created_superchat.frame == superchat_dict1["frame"]

    assert created_superchat.id > 0

    loaded_superchat = Superchat.load(created_superchat.id)
    assert loaded_superchat.frame == superchat_dict1["frame"]


def test_superchat_delete(superchat_item):

    Superchat.delete_id(superchat_item.id)
    c = (
        SuperchatModel.select()
        .where(SuperchatModel.id == superchat_item.id)
        .get_or_none()
    )
    assert c is None


def test_serialize(superchat_item, video_item):
    s = Superchat.serialize(superchat_item.id)
    assert s["frame"] == superchat_item.frame
    assert s["id"] == superchat_item.id
    assert s["video"]["title"] == video_item.title


def test_get_all(superchat_item):
    all_superchats = Superchat.get_all()
    assert len(list(all_superchats)) == 1


def test_update_superchats(superchat_item):
    superchat = Superchat.load(superchat_item.id)
    assert superchat.frame == superchat_item.frame
    Superchat.update({"frame": 15, "id": superchat_item.id})
    assert SuperchatModel.get_by_id(superchat_item.id).frame == 15
