import pytest

from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import Series as SeriesModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.base_repo import Repository
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo

testing_youtube_series_dict = {
    "title": "Some Test YoutubeSeries Title",
    "id": 57312,
}


def test_empty_youtube_series():
    c = YoutubeSeries()
    assert type(c.repo) == YoutubeSeriesRepo


def test_youtube_series_create_and_load(seeded_db):
    series = SeriesModel.select().first()
    testing_youtube_series_dict["series_id"] = series.id

    created_youtube_series = YoutubeSeries.create(testing_youtube_series_dict)
    assert created_youtube_series.title == testing_youtube_series_dict["title"]

    assert created_youtube_series.id > 0

    loaded_youtube_series = YoutubeSeries.load(created_youtube_series.id)
    assert loaded_youtube_series.title == testing_youtube_series_dict["title"]
    assert loaded_youtube_series.id == created_youtube_series.id
    assert loaded_youtube_series.series.title == series.title
    YoutubeSeriesModel.delete_by_id(created_youtube_series.id)


def test_youtube_series_delete(seeded_db):
    series = SeriesModel.select().first()
    testing_youtube_series_dict["series_id"] = series.id

    new_youtube_series = YoutubeSeries.create(testing_youtube_series_dict)
    assert new_youtube_series.id > 0
    YoutubeSeries.delete_id(new_youtube_series.id)


def test_serialize(seeded_db):
    _youtube_series = YoutubeSeriesModel.select().first()
    youtube_series = YoutubeSeries.serialize(_youtube_series.id)

    assert youtube_series["title"] == _youtube_series.title
    assert youtube_series["id"] == _youtube_series.id
    assert youtube_series["series"]["title"] == _youtube_series.series.title


def test_get_all(seeded_db):
    all_youtube_seriess = YoutubeSeries.get_all()
    assert len(list(all_youtube_seriess)) == 3


def test_update_youtube_seriess(seeded_db):
    YOUTUBE_SERIES_ID = 1
    youtube_series = YoutubeSeries.load(YOUTUBE_SERIES_ID)
    orig_title = youtube_series.title
    assert youtube_series.title == "Tech Talks"
    YoutubeSeries.update({"title": "A whole nother title", "id": 1})
    assert (
        YoutubeSeriesModel.get_by_id(YOUTUBE_SERIES_ID).title == "A whole nother title"
    )
    YoutubeSeries.update({"title": orig_title, "id": YOUTUBE_SERIES_ID})
    assert YoutubeSeriesModel.get_by_id(YOUTUBE_SERIES_ID).title == orig_title
