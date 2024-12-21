from pathlib import Path
from unittest.mock import patch

import pytest

from hmtc.domains.series import Series
from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo


def test_youtube_series_create_and_load(youtube_series_dicts, series_dicts):
    sd = series_dicts[0]
    series = Series.create(sd)

    ys = youtube_series_dicts[0]
    ys["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(ys)
    assert youtube_series.instance.title == ys["title"]
    assert youtube_series.instance.id > 0

    loaded_youtube_series = YoutubeSeries.load(youtube_series.instance.id)
    assert loaded_youtube_series.instance.title == ys["title"]
    assert loaded_youtube_series.instance.series_id == series.instance.id
    youtube_series.delete()
    series.delete()


def test_youtube_series_create_no_title(youtube_series_dicts):
    ys = youtube_series_dicts[0]
    del ys["title"]
    try:
        YoutubeSeries.create(ys)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(youtube_series_dicts, series_dicts):
    # setup
    series_dict = series_dicts[1]
    youtube_series_dict = youtube_series_dicts[0]

    series = Series.create(series_dict)
    youtube_series_dict["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(youtube_series_dict)

    # test
    loaded_youtube_series = YoutubeSeries.get_by(id=youtube_series.instance.id)
    assert loaded_youtube_series.instance.title == youtube_series_dict["title"]
    assert loaded_youtube_series.instance.series_id == series.instance.id

    # teardown
    youtube_series.delete()
    series.delete()


def test_get_by_title(youtube_series_dicts, series_dicts):
    # setup
    sd = series_dicts[1]
    series = Series.create(sd)
    ys = youtube_series_dicts[1]
    ys["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(ys)

    # test
    loaded_youtube_series = YoutubeSeries.get_by(title=youtube_series.instance.title)
    assert loaded_youtube_series.instance.title == ys["title"]

    # teardown
    youtube_series.delete()
    series.delete()


def test_select_where(youtube_series_dicts, series_dicts):
    # setup
    series_dict1 = series_dicts[0]
    series_dict2 = series_dicts[1]
    youtube_series_dict1 = youtube_series_dicts[1]
    youtube_series_dict2 = youtube_series_dicts[2]

    series1 = Series.create(series_dict1)
    series2 = Series.create(series_dict2)

    youtube_series_dict1["series_id"] = series1.instance.id
    youtube_series_dict2["series_id"] = series2.instance.id
    youtube_series1 = YoutubeSeries.create(youtube_series_dict1)
    youtube_series2 = YoutubeSeries.create(youtube_series_dict2)

    # tests
    youtube_series_query = YoutubeSeries.select_where(
        title=youtube_series1.instance.title
    )
    assert len(youtube_series_query) == 1
    series_item = YoutubeSeries(youtube_series_query[0].instance.id)
    assert series_item.instance.title == youtube_series_dict1["title"]
    loaded_youtube_series = youtube_series_query[0]
    assert loaded_youtube_series.instance.title == youtube_series_dict1["title"]

    # teardown
    youtube_series1.delete()
    youtube_series2.delete()
    series1.delete()
    series2.delete()


def test_update_youtube_series(youtube_series_dicts, series_dicts):
    # setup
    series_dict = series_dicts[2]
    youtube_series_dict = youtube_series_dicts[2]
    series = Series.create(series_dict)
    youtube_series_dict["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(youtube_series_dict)
    # test
    new_youtube_series = youtube_series.update({"title": "Ozymandias"})

    # verify
    assert youtube_series.instance.title == "Ozymandias"

    youtube_series_from_db = (
        YoutubeSeriesModel.select()
        .where(YoutubeSeriesModel.id == youtube_series.instance.id)
        .get()
    )
    assert youtube_series_from_db.title == "Ozymandias"

    # teardown
    youtube_series.delete()
    series.delete()


def test_youtube_series_delete(youtube_series_dicts, series_dicts):
    series_dict = series_dicts[1]
    youtube_series_dict = youtube_series_dicts[1]
    series = Series.create(series_dict)
    youtube_series_dict["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(youtube_series_dict)

    youtube_series.delete()
    s = (
        YoutubeSeriesModel.select()
        .where(YoutubeSeriesModel.id == youtube_series.instance.id)
        .get_or_none()
    )
    assert s is None


def test_serialize(youtube_series_dicts, series_dicts):
    # setup
    series_dict = series_dicts[2]
    youtube_series_dict = youtube_series_dicts[0]

    series = Series.create(series_dict)
    youtube_series_dict["series_id"] = series.instance.id
    youtube_series = YoutubeSeries.create(youtube_series_dict)

    # tests
    yts = youtube_series.serialize()
    assert yts["title"] == youtube_series_dict["title"]
    assert yts["series"]["id"] == series.instance.id
    assert yts["series"]["title"] == series.instance.title

    # teardown
    youtube_series.delete()
    series.delete()


def test_count(youtube_series_dicts, series_dicts):
    # setup
    series_dict1 = series_dicts[0]
    youtube_series_dict1 = youtube_series_dicts[0]
    youtube_series_dict2 = youtube_series_dicts[1]
    youtube_series_dict3 = youtube_series_dicts[2]

    series = Series.create(series_dict1)
    youtube_series_dict1["series_id"] = series.instance.id
    youtube_series_dict2["series_id"] = series.instance.id
    youtube_series_dict3["series_id"] = series.instance.id

    # tests

    assert YoutubeSeries.count() == 0
    YoutubeSeries.create(youtube_series_dict1)
    YoutubeSeries.create(youtube_series_dict2)
    YoutubeSeries.create(youtube_series_dict3)
    assert YoutubeSeries.count() == 3

    # teardown
    for series_dict in youtube_series_dicts:
        series = YoutubeSeries.get_by(title=series_dict["title"])
        series.delete()

    assert YoutubeSeries.count() == 0
