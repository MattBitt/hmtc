import pytest

from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.section import Section
from hmtc.domains.series import Series
from hmtc.domains.video import Video
from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.domains.track import Track

album_dicts = [
    {"title": "Omegle Bars", "release_date": "2024-09-23"},
    {"title": "Guerrilla Bars", "release_date": "2023-09-23"},
    {"title": "Wordplay Wednesday", "release_date": "2022-09-23"},
]
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

video_dicts = [
    {
        "description": "Harry Mack raps on the street",
        "duration": 400,
        "title": "Guerrilla Bars 1",
        "unique_content": True,
        "upload_date": "2021-01-01",
        "url": "https://www.youtube.com/watch?v=1234",
        "youtube_id": "1234",
        "episode": 1,
        "channel": "Another Harry Mack Channel",
        "series": "Guerrilla",
        "youtube_series": "Guerrilla Bars",
        "album": "Guerrilla Bars",
    },
    {
        "description": "Harry Mack raps on the street",
        "duration": 4000,
        "title": "Wordplay Wednesday 84",
        "unique_content": True,
        "upload_date": "2023-01-01",
        "url": "https://www.youtube.com/watch?v=1234zxcvasd",
        "youtube_id": "1234cvdde",
        "episode": None,
        "channel": "Yet another HM Channel",
        "series": "Livestreams",
        "youtube_series": "Wordplay Wednesday",
        "album": "Wordplay Wednesday",
    },
    {
        "description": "Harry Mack raps on the street",
        "duration": 1200,
        "title": "Omegle Bars 18",
        "unique_content": True,
        "upload_date": "2024-01-01",
        "url": "https://www.youtube.com/watch?v=12345678",
        "youtube_id": "123781",
        "episode": 0,
        "channel": "Clips of harry Mack",
        "series": "Concerts",
        "youtube_series": "Omegle Bars",
        "album": "Omegle Bars",
    },
]

section_dicts = [
    {
        "start": 50,
        "end": 250,
        "section_type": "Intro",
        "video": "Guerrilla Bars 1",
        "track_id": 1,
    },
    {
        "start": 250,
        "end": 350,
        "section_type": "Verse 1",
        "video": "Guerrilla Bars 1",
        "track_id": 2,
    },
    {
        "start": 1000,
        "end": 2000,
        "section_type": "Chorus",
        "video": "Wordplay Wednesday 84",
        "track_id": 3,
    },
]

track_dicts = [
    {
        "id": 1,
        "title": "My First Track",
        "track_number": 1,
        "length": 45,
        "album": "Omegle Bars",
        "video": "Omegle Bars 18",
    },
    {
        "id": 1,
        "title": "My Second Track",
        "track_number": 2,
        "length": 45,
        "album": "Omegle Bars",
        "video": "Omegle Bars 18",
    },
    {
        "id": 3,
        "title": "First Track on different album",
        "track_number": 1,
        "length": 45,
        "album": "Guerrilla Bars",
        "video": "Guerrilla Bars 1",
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


@pytest.fixture(scope="function")
def album_dict1():
    return album_dicts[0]


@pytest.fixture(scope="function")
def album_dict2():
    return album_dicts[1]


@pytest.fixture(scope="function")
def album_dict3():
    return album_dicts[2]


@pytest.fixture(scope="function")
def album_item():
    return Album.create(album_dicts[0])


@pytest.fixture(scope="function")
def section_dict1():
    return section_dicts[0]


@pytest.fixture(scope="function")
def section_dict2():
    return section_dicts[1]


@pytest.fixture(scope="function")
def section_dict3():
    return section_dicts[2]


@pytest.fixture(scope="function")
def section_item(video_item):
    section_dicts[0]["video"] = video_item.title
    return Section.create(section_dicts[0])


@pytest.fixture(scope="function")
def video_dict1():
    return video_dicts[0]


@pytest.fixture(scope="function")
def video_dict2():
    return video_dicts[1]


@pytest.fixture(scope="function")
def video_dict3():
    return video_dicts[2]


@pytest.fixture(scope="function")
def video_item(series_item, youtube_series_item, album_item, channel_item):
    video_dicts[0]["series"] = series_item.title
    video_dicts[0]["youtube_series"] = youtube_series_item.title
    video_dicts[0]["album"] = album_item.title
    video_dicts[0]["channel"] = channel_item.title
    return Video.create(video_dicts[0])


@pytest.fixture(scope="function")
def track_dict1():
    return track_dicts[0]


@pytest.fixture(scope="function")
def track_dict2():
    return track_dicts[1]


@pytest.fixture(scope="function")
def track_dict3():
    return track_dicts[2]


@pytest.fixture(scope="function")
def track_item(video_item, section_item):
    track_dicts[0]["video"] = video_item.title
    track_dicts[0]["album"] = video_item.album.title
    track_dicts[0]["section"] = section_item.id
    return Track.create(track_dicts[0])
