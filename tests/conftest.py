import os
from pathlib import Path

import pytest
from loguru import logger

os.environ["HMTC_ENV"] = "testing"
os.environ["HMTC_CONFIG_PATH"] = "hmtc/config/"
from hmtc.config import init_config
from hmtc.db import create_tables, drop_tables, init_db
from hmtc.models import Video as VideoModel
from hmtc.models import db_null
from hmtc.utils.general import my_copy_file
from hmtc.utils.my_logging import setup_logging

config = init_config()
setup_logging(config)


WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

# this is the actual source of files for tests
INPUT_PATH = STORAGE / "data_for_tests"

# serves as the source of files for future tests to copy from
# i think this is a good idea to keep the original files untouched
STAGING_PATH = WORKING / "files_for_input"
OUTPUT_PATH = WORKING / "files_created_by_testing"


def copy_initial_files():
    if STAGING_PATH.exists():
        if STAGING_PATH.is_dir():
            logger.debug("Removing files from INPUT_PATH before copying new ones.")
            for file in STAGING_PATH.glob("*"):
                file.unlink()
        else:
            STAGING_PATH.unlink()
            STAGING_PATH.mkdir()
    else:
        STAGING_PATH.mkdir()

    initial_files = INPUT_PATH
    assert initial_files.exists()
    assert len(list(initial_files.glob("*"))) > 0
    for file in initial_files.glob("*"):
        my_copy_file(file, STAGING_PATH)
    # need actual files to test with so folder has to be there


@pytest.fixture(scope="function", autouse=True)
def db():
    logger.debug("DB Fixture init")
    db_instance = init_db(db_null, config)
    try:
        create_tables(db_instance)
    except Exception as e:
        logger.error(e)
    yield (db_instance, config)
    drop_tables(db_instance)
    logger.debug("DB Fixture Finish 🎈🎈🎈")


@pytest.fixture(scope="session")
def test_files():
    copy_initial_files()

    logger.debug(f"source_path: {INPUT_PATH}")
    assert INPUT_PATH.exists()
    return [file for file in INPUT_PATH.glob("*")]


@pytest.fixture(scope="function")
def test_image_filename():
    img = [x for x in INPUT_PATH.glob("*.png")][0]

    my_copy_file(img, OUTPUT_PATH)
    return OUTPUT_PATH / img.name


@pytest.fixture(scope="function")
def test_video_filename(test_files):
    vid_file = [x for x in test_files if x.suffix in [".mp4", ".mkv"]][0]

    my_copy_file(vid_file, OUTPUT_PATH)
    return OUTPUT_PATH / vid_file.name


@pytest.fixture(scope="function")
def test_audio_filename(test_files):
    audio_file = [x for x in test_files if x.suffix in [".mp3"]][0]

    my_copy_file(audio_file, OUTPUT_PATH)
    return OUTPUT_PATH / audio_file.name


@pytest.fixture(scope="function")
def test_ww_video_file(test_files):
    video_file = [x for x in test_files if x.stem == "ww100_clip_1_min"][0]

    my_copy_file(video_file, OUTPUT_PATH)
    return OUTPUT_PATH / video_file.name


@pytest.fixture(scope="function")
def test_ww_images(test_files):
    images = [x for x in test_files if x.stem[0:2] == "ww" and x.suffix == ".png"]
    for image in images:
        my_copy_file(image, OUTPUT_PATH)

    return [OUTPUT_PATH / x.name for x in images]


@pytest.fixture(scope="function")
def video():
    return VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
