import pytest

from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository


def test_empty_video():
    c = Video()
    assert type(c.repo) == Repository


def test_video_create_and_load(seeded_db, video_dict):
    channel = ChannelModel(
        title="Test Channel",
        youtube_id="1234q2w43asdf",
        url="https://www.youtube.com/channel/1234",
    )
    channel.save()
    video_dict["_channel"] = channel.my_dict()

    created_video = Video.create(video_dict)
    assert created_video.title == video_dict["title"]
    assert created_video.id > 0
    loaded_video = Video.load(created_video.id)
    assert loaded_video.title == video_dict["title"]

    assert loaded_video.channel.title == video_dict["channel"].title
    Video.delete_id(created_video.id)
    Channel.delete_id(channel.id)


def test_video_delete(seeded_db, video_dict):
    channel = ChannelModel(
        title="Test Channel",
        youtube_id="123545gfdsg4",
        url="https://www.youtube.com/channel/1234",
    )
    channel.save()
    video_dict["_channel"] = channel.my_dict()

    new_video = Video.create(video_dict)

    Video.delete_id(new_video.id)
    Channel.delete_id(channel.id)


def test_serialize(seeded_db):
    _video = VideoModel.select().first()
    video = Video.serialize(_video.id)

    assert video["title"] == _video.title
    assert video["id"] == _video.id
    assert video["channel"]["title"] == _video.channel.title


def test_get_all(seeded_db):
    all_videos = Video.get_all()
    assert len(list(all_videos)) == 4


def test_update_videos(seeded_db):
    VIDEO_ID = 1
    video = VideoModel.select().first()
    orig_title = video.title
    assert video.title == "Metamorphosis | Harry Mack EXCLUSIVE Omegle Bars"
    Video.update({"title": "A whole nother title", "id": 1})
    assert VideoModel.get_by_id(VIDEO_ID).title == "A whole nother title"
    Video.update({"title": orig_title, "id": VIDEO_ID})
    assert VideoModel.get_by_id(VIDEO_ID).title == orig_title
