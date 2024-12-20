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
from hmtc.domains import *
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


@pytest.fixture(scope="session")
def seeded_db(db):
    seed_database_from_json(db)
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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def album_dict() -> dict:
    return {
        "title": "Some Test Album Title",
        "release_date": "2021-01-01",
    }


@pytest.fixture(scope="function")
def youtube_series_dict() -> dict:
    return {
        "title": "Some Test YoutubeSeries Title",
    }


@pytest.fixture(scope="function")
def series_dict() -> dict:
    return {
        "title": "Some Test Series Title",
        "start_date": "2021-01-01",
        "end_date": "2021-12-31",
    }


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


@pytest.fixture(scope="function")
def track_item(
    channel_dict, video_dict, album_dict, disc_dict, track_dict, section_dict
):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()
    video = Video.create(video_dict)
    section_dict["_video"] = video.my_dict()
    section = Section.create(section_dict)

    album = Album.create(album_dict)
    disc_dict["_album"] = album.my_dict()
    disc = Disc.create(disc_dict)
    assert disc.title == disc_dict["title"]

    track_dict["section"] = section.my_dict()
    track_dict["disc"] = disc.my_dict()

    new_track = Track.create(track_dict)
    yield new_track
    Track.delete_id(new_track.id)
    Disc.delete_id(disc.id)
    Album.delete_id(album.id)
    Section.delete_id(section.id)
    Video.delete_id(video.id)
    Channel.delete_id(channel.id)


@pytest.fixture(scope="function")
def video_item(seeded_db, video_dict, channel_dict):
    channel = Channel.create(channel_dict)
    video_dict["_channel"] = channel.my_dict()

    created_video = Video.create(video_dict)
    yield Video.load(created_video.id)
    Video.delete_id(created_video.id)
    Channel.delete_id(channel.id)


### starting refactor on 12/18/24
### fixtures above are the ones i want to keep
### the following are still in use but need to be refactored


# # this is the actual source of files for tests
SOURCE_FILES_PATH = config["STORAGE"] / "data_for_tests"

# # serves as the source of files for future tests to copy from
# # i think this is a good idea to keep the original files untouched
INPUT_PATH = config["WORKING"] / "files_for_input"
OUTPUT_PATH = config["WORKING"] / "files_created_by_testing"


@pytest.fixture(scope="function")
def test_image_filename(test_files):
    img = [x for x in test_files.glob("*") if x.suffix in [".png", ".jpg", ".jpeg"]]
    if len(img) == 0:
        raise FileNotFoundError("No image files found")
    return INPUT_PATH / img[0].name


@pytest.fixture(scope="function")
def test_ww_video_file(test_files):
    video_file = [x for x in test_files.glob("*") if x.stem == "ww100_clip_1_min"][0]
    return INPUT_PATH / video_file.name


def copy_initial_files():
    for files in SOURCE_FILES_PATH.rglob("*Zone.Identifier*"):
        files.unlink()

    if INPUT_PATH.exists():
        remove_tree(INPUT_PATH)

    if OUTPUT_PATH.exists():
        remove_tree(OUTPUT_PATH)

    initial_files = SOURCE_FILES_PATH
    assert initial_files.exists()
    assert len(list(initial_files.rglob("*"))) > 0

    copy_tree(SOURCE_FILES_PATH, INPUT_PATH)
    OUTPUT_PATH.mkdir(exist_ok=True, parents=True)


@pytest.fixture(scope="session")
def test_files():
    copy_initial_files()
    return INPUT_PATH


@pytest.fixture(scope="function")
def test_audio_filename(test_files):
    audio_file = [x for x in test_files.glob("*") if x.suffix in [".mp3"]][0]

    return INPUT_PATH / audio_file.name
