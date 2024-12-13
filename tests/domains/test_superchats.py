import pytest

from hmtc.domains.superchat import Superchat
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

testing_superchat_dict = {
    "id": 80765,
    "frame": 1013,
}


def test_empty_superchat():
    c = Superchat()
    assert type(c.repo) == Repository


def test_superchat_create_and_load(seeded_db):
    video = VideoModel.select().first()
    testing_superchat_dict["video_id"] = video.id
    created_superchat = Superchat.create(testing_superchat_dict)
    assert created_superchat.frame == testing_superchat_dict["frame"]

    assert created_superchat.id > 0

    loaded_superchat = Superchat.load(created_superchat.id)
    assert loaded_superchat.frame == testing_superchat_dict["frame"]
    assert loaded_superchat.video.title == video.title
    Superchat.delete_id(created_superchat.id)


def test_superchat_delete(seeded_db):
    video = VideoModel.select().first()
    testing_superchat_dict["video_id"] = video.id
    new_superchat = Superchat.create(testing_superchat_dict)
    assert new_superchat.id > 0
    Superchat.delete_id(new_superchat.id)


def test_serialize(seeded_db):
    _superchat = SuperchatModel.select().first()
    superchat = Superchat.serialize(_superchat.id)

    assert superchat["frame"] == _superchat.frame
    assert superchat["id"] == _superchat.id
    assert superchat["video"]["title"] == _superchat.video.title


def test_get_all(seeded_db):
    all_superchats = Superchat.get_all()
    assert len(list(all_superchats)) == 3


def test_update_superchats(seeded_db):
    SUPERCHAT_ID = 1
    superchat = Superchat.load(SUPERCHAT_ID)
    orig_frame = superchat.frame
    assert superchat.frame == 10
    Superchat.update({"frame": 15, "id": 1})
    assert SuperchatModel.get_by_id(SUPERCHAT_ID).frame == 15
    Superchat.update({"frame": orig_frame, "id": SUPERCHAT_ID})
    assert SuperchatModel.get_by_id(SUPERCHAT_ID).frame == orig_frame
