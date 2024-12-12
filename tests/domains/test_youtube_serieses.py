import pytest

from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.base_repo import Repository
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo
from tests.domains.fixtures import (
    series_item,
    youtube_series_dict1,
    youtube_series_dict2,
    youtube_series_dict3,
    youtube_series_item,
)


def test_empty_youtube_series():
    c = YoutubeSeries()
    assert type(c.repo) == YoutubeSeriesRepo


def test_youtube_series_create_and_load(youtube_series_dict1, series_item):
    youtube_series_dict1["series_id"] = series_item.id
    created_youtube_series = YoutubeSeries.create(youtube_series_dict1)
    assert created_youtube_series.title == youtube_series_dict1["title"]

    assert created_youtube_series.id > 0

    loaded_youtube_series = YoutubeSeries.load(created_youtube_series.id)
    assert loaded_youtube_series.title == youtube_series_dict1["title"]


def test_youtube_series_delete(youtube_series_item):

    YoutubeSeries.delete_id(youtube_series_item.id)
    c = (
        YoutubeSeriesModel.select()
        .where(YoutubeSeriesModel.id == youtube_series_item.id)
        .get_or_none()
    )
    assert c is None


def test_serialize(youtube_series_item):
    s = YoutubeSeries.serialize(youtube_series_item.id)
    assert s["title"] == youtube_series_item.title
    assert s["id"] == youtube_series_item.id


def test_get_all(youtube_series_item):
    all_youtube_seriess = YoutubeSeries.get_all()
    assert len(list(all_youtube_seriess)) == 1


def test_update_youtube_seriess(youtube_series_item):
    youtube_series = YoutubeSeries.load(youtube_series_item.id)
    assert youtube_series.title == youtube_series_item.title
    YoutubeSeries.update(
        {"title": "A whole nother title", "id": youtube_series_item.id}
    )
    assert (
        YoutubeSeriesModel.get_by_id(youtube_series_item.id).title
        == "A whole nother title"
    )


def test_get_youtube_series_videos():
    youtube_series = YoutubeSeries()
    videos = youtube_series.repo.videos()
    assert len(list(videos)) == 0
    # assert False
