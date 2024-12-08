import pytest
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.youtube_series import YoutubeSeries

channel_dicts = [
    {
        "title": "Clips of harry Mack",
        "url": "https://www.youtube.com/channel/erwhgfdhfadsf",
        "youtube_id": "erwhgfdhfadsf",
        "auto_update": True,
        "last_update_completed": "2021-12-01 00:00:00",
    },
    {
        "title": "Yet another HM Channel",
        "url": "https://www.youtube.com/channel/cvbcxvnbbncvbgfds",
        "youtube_id": "cvbcxvnbbncvbgfds",
        "auto_update": True,
        "last_update_completed": "2024-12-01 00:00:00",
    },
    {
        "title": "Another Harry Mack Channel",
        "url": "https://www.youtube.com/channel/hjklhgjefvcxzv",
        "youtube_id": "'hjklhgjefvcxzv'",
        "auto_update": False,
        "last_update_completed": "2023-12-01 00:00:00",
    },
]

series_dicts = [
    {
        "title": "Guerrilla",
        "start_date": "2021-01-01",
        "end_date": "2021-12-31",
    },
    {
        "title": "Livestreams",
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
    },
    {
        "title": "Concerts",
        "start_date": "2019-01-01",
        "end_date": "2015-12-31",
    },
]

youtube_series_dicts = [
    {
        "title": "Guerrilla Bars",
        "series": "Guerrilla",
    },
    {
        "title": "Wordplay Wednesday",
        "series": "Livestreams",
    },
    {
        "title": "Omegle Bars",
        "series": "Livestreams",
    },
]


@pytest.fixture(scope="function")
def channel_dict1():
    return channel_dicts[0]


@pytest.fixture(scope="function")
def channel_dict2():
    return channel_dicts[1]


@pytest.fixture(scope="function")
def channel_dict3():
    return channel_dicts[2]


@pytest.fixture(scope="function")
def channel_item():
    return Channel().create(channel_dicts[0])


@pytest.fixture(scope="function")
def series_dict1():
    return series_dicts[0]


@pytest.fixture(scope="function")
def series_dict2():
    return series_dicts[1]


@pytest.fixture(scope="function")
def series_dict3():
    return series_dicts[2]


@pytest.fixture(scope="function")
def series_item():
    return Series.create(series_dicts[0])


@pytest.fixture(scope="function")
def youtube_series_dict1():
    return youtube_series_dicts[0]


@pytest.fixture(scope="function")
def youtube_series_dict2():
    return youtube_series_dicts[1]


@pytest.fixture(scope="function")
def youtube_series_dict3():
    return youtube_series_dicts[2]


@pytest.fixture(scope="function")
def youtube_series_item(series_item):
    youtube_series_dicts[0]["series"] = series_item.title
    yts = YoutubeSeries.create(youtube_series_dicts[0])
    return yts
