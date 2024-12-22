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
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
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


@pytest.fixture(scope="function")
def artist_dict() -> dict:
    return {
        "name": "Some Test Artist",
        "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
    }


@pytest.fixture(scope="function")
def beat_dict() -> dict:
    return {
        "title": "Some Test Beat Title",
    }


@pytest.fixture(scope="function")
def video_dict() -> dict:
    return {
        "description": "This is only for testing.in the files tab.",
        "duration": 400,
        "title": "Another quirky title to stand out.",
        "unique_content": True,
        "upload_date": "2021-01-01",
        "url": "https://www.youtube.com/watch?v=1234vzcxvadsf",
        "youtube_id": "vjhfadsklfhew",
    }


@pytest.fixture(scope="function")
def album_dict() -> dict:
    return {
        "title": "Some Test Album Title",
        "release_date": "2021-01-01",
    }


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


@pytest.fixture(scope="function")
def user_dict() -> dict:
    return {
        "id": 101,
        "username": "testuser",
        "email": "asdf@jkqwer.com",
        "hashed_password": "1234",
        "jellyfin_id": "1234",
    }


@pytest.fixture(scope="function")
def track_dict() -> dict:
    return {
        "title": "Random Track Title",
        "length": 1000,
        "track_number": 1,
        "track_number_verbose": "001",
    }


@pytest.fixture(scope="function")
def section_dict() -> dict:
    return {
        "start": 0,
        "end": 100,
        "section_type": "verse",
    }


@pytest.fixture(scope="function")
def channel_dicts() -> list:
    return [
        {
            "title": "Marmalade Channel",
            "url": "https://www.youtube.com/channel/1234vz7654363cxvadsf",
            "youtube_id": "hkjfaesdl",
            "auto_update": True,
            "last_update_completed": "2021-01-01T00:00:00",
        },
        {
            "title": "Peanut Butter Channel",
            "url": "https://www.youtube.com/channel/12sgbbvfsdgfd34vzcxvadsf",
            "youtube_id": "vcxzrtfd",
            "auto_update": True,
            "last_update_completed": "2021-01-01T00:00:00",
        },
        {
            "title": "Jelly Channel",
            "url": "https://www.youtube.com/channel/1234fdsag546xvadsf",
            "youtube_id": "trrewtghf",
            "auto_update": True,
            "last_update_completed": "2021-01-01T00:00:00",
        },
    ]


@pytest.fixture(scope="function")
def disc_dict() -> dict:
    return {
        "title": "Another Random Disc in Testing",
    }


@pytest.fixture(scope="function")
def superchat_dict() -> dict:
    return {
        "frame": 15,
    }


@pytest.fixture(scope="function")
def superchat_segment_dict() -> dict:
    return {
        "start_time_ms": 0,
        "end_time_ms": 10,
    }


@pytest.fixture(scope="function")
def topic_dict() -> dict:
    return {
        "text": "apple",
    }
