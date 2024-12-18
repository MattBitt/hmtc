import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.superchat import Superchat
from hmtc.domains.video import Video
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


def test_empty_superchat():
    c = Superchat()
    assert type(c.repo) == Repository


def test_superchat_create_and_load(seeded_db, channel_dict, video_dict, superchat_dict):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()
    video = Video.create(video_dict)
    superchat_dict["_video"] = video.my_dict()
    created_superchat = Superchat.create(superchat_dict)
    assert created_superchat.frame == superchat_dict["frame"]

    assert created_superchat.id > 0

    loaded_superchat = Superchat.load(created_superchat.id)
    assert loaded_superchat.frame == superchat_dict["frame"]
    assert loaded_superchat.video.title == video.title
    Superchat.delete_id(created_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_superchat_delete(seeded_db, channel_dict, video_dict, superchat_dict):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()
    video = Video.create(video_dict)
    superchat_dict["_video"] = video.my_dict()
    new_superchat = Superchat.create(superchat_dict)
    assert new_superchat.id > 0
    Superchat.delete_id(new_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db, channel_dict, video_dict, superchat_dict):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()
    video = Video.create(video_dict)
    superchat_dict["_video"] = video.my_dict()
    _superchat = Superchat.create(superchat_dict)
    superchat = Superchat.serialize(_superchat.id)

    assert superchat["frame"] == _superchat.frame
    assert superchat["id"] == _superchat.id
    assert superchat["video"]["title"] == _superchat.video.title
    Superchat.delete_id(_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_get_all(seeded_db):
    all_superchats = Superchat.get_all()
    assert len(list(all_superchats)) == 0


def test_update_superchats(seeded_db, superchat_dict, video_item):

    superchat_dict["_video"] = video_item.my_dict()
    _superchat = Superchat.create(superchat_dict)
    original_frame = _superchat.frame
    Superchat.update({"frame": 15, "id": _superchat.id})
    assert SuperchatModel.get_by_id(_superchat.id).frame == 15
    Superchat.update({"frame": original_frame, "id": _superchat.id})
    assert SuperchatModel.get_by_id(_superchat.id).frame == original_frame
    Superchat.delete_id(_superchat.id)
