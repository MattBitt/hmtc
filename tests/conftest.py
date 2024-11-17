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
SOURCE_FILES_PATH = STORAGE / "data_for_tests"

# serves as the source of files for future tests to copy from
# i think this is a good idea to keep the original files untouched
INPUT_PATH = WORKING / "files_for_input"
OUTPUT_PATH = WORKING / "files_created_by_testing"


def copy_initial_files():
    if INPUT_PATH.exists():
        if INPUT_PATH.is_dir():

            for file in INPUT_PATH.glob("*"):
                file.unlink()
        else:
            INPUT_PATH.unlink()
            INPUT_PATH.mkdir()
    else:
        INPUT_PATH.mkdir()

    initial_files = SOURCE_FILES_PATH
    assert initial_files.exists()
    assert len(list(initial_files.rglob("*"))) > 0
    for file in initial_files.rglob("*"):
        my_copy_file(file, INPUT_PATH)


@pytest.fixture(scope="function", autouse=True)
def db():
    db_instance = init_db(db_null, config)
    try:
        create_tables(db_instance)
    except Exception as e:
        logger.error(e)
    yield (db_instance, config)
    drop_tables(db_instance)


@pytest.fixture(scope="function")
def test_files():
    # copies files from SOURCE_FILES_PATH to INPUT_PATH
    copy_initial_files()
    assert INPUT_PATH.exists()
    files = [file for file in INPUT_PATH.rglob("*")]
    return files


@pytest.fixture(scope="function")
def test_image_filename(test_files):
    img = [x for x in test_files if x.suffix in [".png", ".jpg", ".jpeg"]][0]

    my_copy_file(img, INPUT_PATH)
    return INPUT_PATH / img.name


@pytest.fixture(scope="function")
def test_video_filename(test_files):
    vid_file = [x for x in test_files if x.suffix in [".mp4", ".mkv"]][0]

    my_copy_file(vid_file, INPUT_PATH)
    return INPUT_PATH / vid_file.name


@pytest.fixture(scope="function")
def test_audio_filename(test_files):
    audio_file = [x for x in test_files if x.suffix in [".mp3"]][0]

    my_copy_file(audio_file, INPUT_PATH)
    return INPUT_PATH / audio_file.name


@pytest.fixture(scope="function")
def test_ww_video_file(test_files):
    video_file = [x for x in test_files if x.stem == "ww100_clip_1_min"][0]

    my_copy_file(video_file, INPUT_PATH)
    return INPUT_PATH / video_file.name


@pytest.fixture(scope="function")
def test_ww_images(test_files):
    test_images = [x for x in test_files if "random" in x.stem and x.suffix == ".jpg"][
        :100
    ]

    for image in test_images:
        my_copy_file(image, INPUT_PATH)
    ww_images = [INPUT_PATH / x.name for x in test_images]
    return ww_images


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
