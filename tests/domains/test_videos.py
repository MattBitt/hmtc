import pytest

from hmtc.domains.video import Video
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository
from tests.domains.fixtures import (
    album_item,
    channel_item,
    series_item,
    video_dict1,
    video_dict2,
    video_dict3,
    video_item,
    youtube_series_item,
)


def test_empty_video():
    c = Video()
    assert type(c.repo) == Repository


def test_video_create_and_load(
    video_dict1, series_item, youtube_series_item, album_item, channel_item
):
    # setup relationships
    video_dict1["series"] = series_item.title
    video_dict1["youtube_series"] = youtube_series_item.title
    video_dict1["album"] = album_item.title
    video_dict1["channel"] = channel_item.title

    created_video = Video.create(video_dict1)
    assert created_video.title == video_dict1["title"]
    assert created_video.id > 0

    loaded_video = Video.load(created_video.id)
    assert loaded_video.title == video_dict1["title"]
    assert loaded_video.series.title == series_item.title
    assert loaded_video.youtube_series.title == youtube_series_item.title
    assert loaded_video.album.title == album_item.title
    assert loaded_video.channel.title == channel_item.title


def test_video_delete(video_item):

    Video.delete_id(video_item.id)
    c = VideoModel.select().where(VideoModel.id == video_item.id).get_or_none()
    assert c is None


def test_serialize(video_item):
    s = Video.serialize(video_item.id)
    assert s["title"] == video_item.title
    assert s["id"] == video_item.id


def test_get_all(video_item):
    all_videos = Video.get_all()
    assert len(list(all_videos)) == 1


def test_update_videos(video_item):
    video = Video.load(video_item.id)
    assert video.title == video_item.title
    Video.update({"title": "A whole nother title", "id": video_item.id})
    assert VideoModel.get_by_id(video_item.id).title == "A whole nother title"
