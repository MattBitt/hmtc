import os
from pathlib import Path

import numpy as np
import pytest
from loguru import logger
from PIL import Image

# these are needed before the app imports to set the environment variables
os.environ["HMTC_ENV"] = "testing"


from hmtc.config import init_config
from hmtc.db import create_tables, drop_all_tables, init_db
from hmtc.domains import (
    Album,
    Artist,
    Beat,
    Channel,
    Disc,
    Section,
    Series,
    Superchat,
    SuperchatSegment,
    Topic,
    Track,
    User,
    Video,
)
from hmtc.models import db_null
from hmtc.utils.db_migrator import run_migrations
from hmtc.utils.general import copy_tree, remove_tree
from hmtc.utils.importer.seed_database import seed_database_from_json
from hmtc.utils.my_logging import setup_logging

config = init_config()
setup_logging(config)


@pytest.fixture(scope="session")
def db():
    db_instance = init_db(db_null, config)
    try:
        create_tables(db_instance)
        run_migrations(db_instance)
    except Exception as e:
        logger.error(e)
    yield (db_instance, config)
    drop_all_tables(db_instance)


@pytest.fixture(autouse=True, scope="session")
def empty_db(db):
    return db


@pytest.fixture(scope="function")
def text_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("This is a test file. blah")
    yield file
    file.unlink()


@pytest.fixture
def album_dicts():
    return [
        {"title": "Album 1", "release_date": "2023-01-01"},
        {"title": "Album 2", "release_date": "2023-01-02"},
        {"title": "Album 3", "release_date": "2023-01-03"},
    ]


@pytest.fixture(scope="function")
def channel_dicts() -> list:
    return [
        {
            "title": "Marmalade Channel",
            "url": "https://www.youtube.com/channel/1234vz7654363cxvadsf",
            "youtube_id": "hkjfaesdl",
            "auto_update": True,
            "last_update_completed": "2021-01-01 00:00:00",
        },
        {
            "title": "Peanut Butter Channel",
            "url": "https://www.youtube.com/channel/12sgbbvfsdgfd34vzcxvadsf",
            "youtube_id": "vcxzrtfd",
            "auto_update": True,
            "last_update_completed": "2021-01-01 00:00:00",
        },
        {
            "title": "Jelly Channel",
            "url": "https://www.youtube.com/channel/1234fdsag546xvadsf",
            "youtube_id": "trrewtghf",
            "auto_update": True,
            "last_update_completed": "2021-01-01 00:00:00",
        },
    ]


@pytest.fixture
def disc_dicts():

    return [
        {"title": "Disc 1"},
        {"title": "Disc 2"},
        {"title": "Disc 3"},
    ]


@pytest.fixture
def section_dicts():
    return [
        {"start": 0, "end": 100, "section_type": "intro"},
        {"start": 100, "end": 200, "section_type": "main"},
        {"start": 200, "end": 300, "section_type": "outro"},
    ]


@pytest.fixture(scope="function")
def series_dicts() -> list:
    return [
        {
            "title": "Some Test Series Title",
            "start_date": "2021-01-01",
            "end_date": "2021-12-31",
        },
        {
            "title": "Another Test Series Title",
            "start_date": "2021-01-01",
            "end_date": "2021-12-31",
        },
        {
            "title": "Yet Another Test Series Title",
            "start_date": "2021-01-01",
            "end_date": "2021-12-31",
        },
    ]


@pytest.fixture
def superchat_dicts() -> list:
    return [
        {"frame": 0},
        {"frame": 10},
        {"frame": 20},
    ]


@pytest.fixture
def superchat_segment_dicts() -> list:
    return [
        {"start_time_ms": 0, "end_time_ms": 100},
        {"start_time_ms": 100, "end_time_ms": 200},
        {"start_time_ms": 200, "end_time_ms": 300},
    ]


@pytest.fixture
def track_dicts():
    return [
        {"title": "Track 1", "track_number": 1, "length": 100},
        {"title": "Track 2", "track_number": 2, "length": 200},
        {"title": "Track 3", "track_number": 3, "length": 300},
    ]


@pytest.fixture
def video_dicts():
    return [
        {
            "title": "Video 1",
            "description": "Description 1",
            "duration": 100,
            "upload_date": "2023-01-01",
            "url": "http://example.com/video1",
            "youtube_id": "vid1",
        },
        {
            "title": "Video 2",
            "description": "Description 2",
            "duration": 200,
            "upload_date": "2023-01-02",
            "url": "http://example.com/video2",
            "youtube_id": "vid2",
        },
        {
            "title": "Video 3",
            "description": "Description 3",
            "duration": 300,
            "upload_date": "2023-01-03",
            "url": "http://example.com/video3",
            "youtube_id": "vid3",
        },
    ]


@pytest.fixture(scope="function")
def youtube_series_dicts():
    return [
        {
            "title": "Episodic Series 137",
            "url": "http://example.com/series1",
            "youtube_id": "series1_id",
            "auto_update": True,
            "last_update_completed": "2023-01-01",
        },
        {
            "title": "Chimpanzee Bars 112",
            "url": "http://example.com/series2",
            "youtube_id": "series2_id",
            "auto_update": False,
            "last_update_completed": "2023-01-02",
        },
        {
            "title": "Mack Saves Christmas 3",
            "url": "http://example.com/series3",
            "youtube_id": "series3_id",
            "auto_update": True,
            "last_update_completed": "2023-01-03",
        },
    ]


@pytest.fixture
def album_item(album_dicts):
    album = Album.create(album_dicts[0])
    yield album
    album.delete()


@pytest.fixture
def channel_item(channel_dicts):
    channel = Channel.create(channel_dicts[0])
    yield channel
    channel.delete()


@pytest.fixture
def disc_item(disc_dicts, album_item):
    dd = disc_dicts[0]
    dd["album_id"] = album_item.instance.id
    created_disc = Disc.create(dd)
    yield created_disc
    created_disc.delete()


@pytest.fixture
def section_item(section_dicts, video_item):
    sd = section_dicts[0]
    sd["video_id"] = video_item.instance.id
    created_section = Section.create(sd)
    yield created_section
    created_section.delete()


@pytest.fixture
def series_item(series_dicts):
    series = Series.create(series_dicts[0])
    yield series
    series.delete()


@pytest.fixture
def superchat_item(superchat_dicts, video_item):
    sd = superchat_dicts[0]
    sd["video_id"] = video_item.instance.id
    superchat = Superchat.create(sd)
    yield superchat
    superchat.delete()


@pytest.fixture
def superchat_segment_item(superchat_segment_dicts, section_item):
    ssd = superchat_segment_dicts[0]
    ssd["section_id"] = section_item.instance.id
    created_superchat_segment = SuperchatSegment.create(ssd)
    yield created_superchat_segment
    created_superchat_segment.delete()


@pytest.fixture
def track_item(track_dicts, disc_item, section_item):
    td = track_dicts[0]
    td["disc_id"] = disc_item.instance.id
    td["section_id"] = section_item.instance.id
    created_track = Track.create(td)
    yield created_track
    created_track.delete()


@pytest.fixture
def video_item(video_dicts, channel_item):
    video_dicts[0]["channel_id"] = channel_item.instance.id
    video = Video.create(video_dicts[0])
    yield video
    video.delete()


@pytest.fixture
def youtube_series_item(youtube_series_dicts):
    series = Series.create(youtube_series_dicts[0])
    yield series
    series.delete()


@pytest.fixture
def artist_dicts() -> list:
    return [
        {"name": "Artist 1", "url": "http://example.com/artist1"},
        {"name": "Artist 2", "url": "http://example.com/artist2"},
        {"name": "Artist 3", "url": "http://example.com/artist3"},
    ]


@pytest.fixture
def artist_item(artist_dicts):
    artist = Artist.create(artist_dicts[0])
    yield artist
    artist.delete()


@pytest.fixture
def beat_dicts() -> list:
    return [
        {"title": "Beat 1"},
        {"title": "Beat 2"},
        {"title": "Beat 3"},
    ]


@pytest.fixture
def beat_item(beat_dicts):
    beat = Beat.create(beat_dicts[0])
    yield beat
    beat.delete()


@pytest.fixture
def user_dicts() -> list:
    return [
        {
            "username": "user1",
            "email": "user1@example.com",
            "hashed_password": "hashed_pw1",
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "hashed_password": "hashed_pw2",
        },
        {
            "username": "user3",
            "email": "user3@example.com",
            "hashed_password": "hashed_pw3",
        },
    ]


@pytest.fixture
def user_item(user_dicts):
    user = User.create(user_dicts[0])
    yield user
    user.delete()


@pytest.fixture
def topic_dicts() -> list:
    return [
        {"text": "Topic 1"},
        {"text": "Topic 2"},
        {"text": "Topic 3"},
    ]


@pytest.fixture
def topic_item(topic_dicts):
    topic = Topic.create(topic_dicts[0])
    yield topic
    topic.delete()
