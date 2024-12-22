import pytest
from hmtc.domains.superchat import Superchat
from hmtc.models import Superchat as SuperchatModel
from hmtc.domains.video import Video


def test_superchat_create_and_load(superchat_dicts, video_item):
    # setup
    sd = superchat_dicts[0]
    sd["video_id"] = video_item.instance.id
    created_superchat = Superchat.create(sd)

    # test
    assert created_superchat.instance.frame == sd["frame"]
    assert created_superchat.instance.id > 0

    loaded_superchat = Superchat.load(created_superchat.instance.id)
    assert loaded_superchat.instance.frame == sd["frame"]
    # teardown
    created_superchat.delete()


def test_superchat_create_no_frame(superchat_dicts):
    sd = superchat_dicts[0]
    del sd["frame"]
    try:
        Superchat.create(sd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(superchat_item):
    loaded_superchat = Superchat.get_by(id=superchat_item.instance.id)
    assert loaded_superchat.instance.frame == superchat_item.instance.frame


def test_get_by_frame(superchat_item):
    loaded_superchat = Superchat.get_by(frame=superchat_item.instance.frame)
    assert loaded_superchat.instance.frame == superchat_item.instance.frame


def test_select_where(superchat_item):
    superchat_query = Superchat.select_where(frame=superchat_item.instance.frame)
    assert len(superchat_query) == 1
    superchat = superchat_query[0]
    assert superchat.instance.frame == superchat_item.instance.frame


def test_update_superchat(superchat_item):
    superchat = superchat_item
    new_superchat = superchat.update({"frame": 100})
    assert new_superchat.instance.frame == 100

    superchat_from_db = (
        SuperchatModel.select().where(SuperchatModel.id == superchat.instance.id).get()
    )
    assert superchat_from_db.frame == 100


def test_superchat_delete(superchat_item):
    superchat = superchat_item
    superchat.delete()
    s = (
        SuperchatModel.select()
        .where(SuperchatModel.id == superchat_item.instance.id)
        .get_or_none()
    )
    assert s is None


def test_serialize(superchat_item):
    s = superchat_item.serialize()
    assert s["frame"] == superchat_item.instance.frame


def test_count(superchat_dicts, video_item):
    sd1 = superchat_dicts[0]
    sd1["video_id"] = video_item.instance.id
    sd2 = superchat_dicts[1]
    sd2["video_id"] = video_item.instance.id
    sd3 = superchat_dicts[2]
    sd3["video_id"] = video_item.instance.id

    assert Superchat.count() == 0
    Superchat.create(sd1)
    Superchat.create(sd2)
    Superchat.create(sd3)
    assert Superchat.count() == 3

    for superchat_dict in superchat_dicts:
        superchat = Superchat.get_by(frame=superchat_dict["frame"])
        superchat.delete()

    assert Superchat.count() == 0
