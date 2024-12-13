import pytest

from hmtc.domains.video import Video
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository

testing_video_dict = {
    "id": 984256,
    "description": "This is only for testing. If you see this on the website, something is wrong.",
    "duration": 400,
    "title": "Some Test Titile that i just made up",
    "unique_content": True,
    "upload_date": "2021-01-01",
    "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
    "youtube_id": "1234adfaewr",
}


def test_empty_video():
    c = Video()
    assert type(c.repo) == Repository


def test_video_create_and_load(seeded_db):
    channel = ChannelModel.select().first()
    testing_video_dict["channel_id"] = channel.id

    created_video = Video.create(testing_video_dict)
    assert created_video.title == testing_video_dict["title"]
    assert created_video.id > 0

    loaded_video = Video.load(created_video.id)
    assert loaded_video.title == testing_video_dict["title"]
    # ???
    assert loaded_video.channel.title == testing_video_dict["channel"].title
    Video.delete_id(created_video.id)


def test_video_delete(seeded_db):
    channel = ChannelModel.select().first()
    testing_video_dict["channel_id"] = channel.id

    new_video = Video.create(testing_video_dict)

    Video.delete_id(new_video.id)


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
    video = Video.load(VIDEO_ID)
    orig_title = video.title
    assert video.title == "Omegle Bars 88"
    Video.update({"title": "A whole nother title", "id": 1})
    assert VideoModel.get_by_id(VIDEO_ID).title == "A whole nother title"
    Video.update({"title": orig_title, "id": VIDEO_ID})
    assert VideoModel.get_by_id(VIDEO_ID).title == orig_title
