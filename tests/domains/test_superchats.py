import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.superchat import Superchat
from hmtc.domains.video import Video
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

testing_superchat_dict = {
    "frame": 1013,
}

testing_video_dict = {
    "title": "Some Test Video Title",
    "description": "Some Test Video Description",
    "url": "https://www.youtube.com/watch?v=123456",
    "youtube_id": "vcbfdareq",
    "duration": 100,
    "upload_date": "2021-01-01",
}

testing_channel_dict = {
    "title": "Another Test Channel Title",
    "url": "https://www.youtube.com/channel/1234vzcxvadsf",
    "youtube_id": "kklhjoiuygf",
    "auto_update": True,
    "last_update_completed": "2021-01-01 00:00:00",
}


def test_empty_superchat():
    c = Superchat()
    assert type(c.repo) == Repository


def test_superchat_create_and_load(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_superchat_dict["_video"] = video.my_dict()
    created_superchat = Superchat.create(testing_superchat_dict)
    assert created_superchat.frame == testing_superchat_dict["frame"]

    assert created_superchat.id > 0

    loaded_superchat = Superchat.load(created_superchat.id)
    assert loaded_superchat.frame == testing_superchat_dict["frame"]
    assert loaded_superchat.video.title == video.title
    Superchat.delete_id(created_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_superchat_delete(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_superchat_dict["_video"] = video.my_dict()
    new_superchat = Superchat.create(testing_superchat_dict)
    assert new_superchat.id > 0
    Superchat.delete_id(new_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_superchat_dict["_video"] = video.my_dict()
    _superchat = Superchat.create(testing_superchat_dict)
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


def test_update_superchats(seeded_db):
    channel = Channel.create(testing_channel_dict)
    testing_video_dict["_channel"] = channel.my_dict()
    video = Video.create(testing_video_dict)
    testing_superchat_dict["_video"] = video.my_dict()
    _superchat = Superchat.create(testing_superchat_dict)
    original_frame = _superchat.frame
    Superchat.update({"frame": 15, "id": _superchat.id})
    assert SuperchatModel.get_by_id(_superchat.id).frame == 15
    Superchat.update({"frame": original_frame, "id": _superchat.id})
    assert SuperchatModel.get_by_id(_superchat.id).frame == original_frame
    Superchat.delete_id(_superchat.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)
