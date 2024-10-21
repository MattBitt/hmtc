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

SOURCE_PATH = WORKING / "test_file_input"

TARGET_PATH = WORKING / "test_file_output"
TARGET_PATH.mkdir(exist_ok=True)


def copy_initial_files():
    if SOURCE_PATH.exists():
        logger.debug("Removing files from SOURCE_PATH before copying new ones.")
        for file in SOURCE_PATH.glob("*"):
            file.unlink()

    init_files = STORAGE / "data_for_tests"
    assert init_files.exists()

    for file in init_files.glob("*"):
        my_copy_file(file, SOURCE_PATH)
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

    logger.debug(f"source_path: {SOURCE_PATH}")
    assert SOURCE_PATH.exists()
    return [file for file in SOURCE_PATH.glob("*")]


@pytest.fixture(scope="function")
def test_image_filename():
    img = [x for x in SOURCE_PATH.glob("*.png")][0]

    my_copy_file(img, TARGET_PATH)
    return TARGET_PATH / img.name


@pytest.fixture(scope="function")
def test_video_filename(test_files):
    vid_file = [x for x in test_files if x.suffix in [".mp4", ".mkv"]][0]

    my_copy_file(vid_file, TARGET_PATH)
    return TARGET_PATH / vid_file.name


@pytest.fixture(scope="function")
def test_audio_filename(test_files):
    audio_file = [x for x in test_files if x.suffix in [".mp3"]][0]

    my_copy_file(audio_file, TARGET_PATH)
    return TARGET_PATH / audio_file.name


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


# @pytest.fixture
# def caplog(_caplog):
#     class PropogateHandler(logging.Handler):
#         def emit(self, record):
#             logging.getLogger(record.name).handle(record)

#     handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
#     yield _caplog
#     logger.remove(handler_id)
