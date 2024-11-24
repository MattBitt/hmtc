import os
from pathlib import Path

import numpy as np
import pytest
from loguru import logger
from PIL import Image

os.environ["HMTC_ENV"] = "testing"
os.environ["HMTC_CONFIG_PATH"] = "hmtc/config/"
from hmtc.config import init_config
from hmtc.db import create_tables, drop_tables, init_db
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.models import db_null
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.utils.general import copy_tree, my_copy_file, remove_tree
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


@pytest.fixture(scope="function", autouse=True)
def db():
    db_instance = init_db(db_null, config)
    try:
        create_tables(db_instance)
    except Exception as e:
        logger.error(e)
    yield (db_instance, config)
    drop_tables(db_instance)


@pytest.fixture(scope="session")
def test_files():
    copy_initial_files()
    return INPUT_PATH


@pytest.fixture(scope="function")
def test_image_filename(test_files):
    img = [x for x in test_files.glob("*") if x.suffix in [".png", ".jpg", ".jpeg"]]
    if len(img) == 0:
        raise FileNotFoundError("No image files found")
    return INPUT_PATH / img[0].name


@pytest.fixture(scope="function")
def test_video_filename(test_files):
    vid_file = [x for x in test_files.glob("*") if x.suffix in [".mp4", ".mkv"]][0]

    return INPUT_PATH / vid_file.name


@pytest.fixture(scope="function")
def test_audio_filename(test_files):
    audio_file = [x for x in test_files.glob("*") if x.suffix in [".mp3"]][0]

    return INPUT_PATH / audio_file.name


@pytest.fixture(scope="function")
def test_ww_video_file(test_files):
    video_file = [x for x in test_files.glob("*") if x.stem == "ww100_clip_1_min"][0]
    return INPUT_PATH / video_file.name


@pytest.fixture(scope="function")
def test_ww_video_file2(test_files):
    video_file = [x for x in test_files.glob("*") if x.stem == "ww100_clip_1_min2"][0]
    return INPUT_PATH / video_file.name


@pytest.fixture(scope="function")
def test_ww116_images(test_files):
    ww116_folder = test_files / "ww_screenshots" / "ww116"
    assert ww116_folder.exists()
    has_superchats = [x for x in (ww116_folder / "has_superchat").glob("*")]
    no_superchats = [x for x in (ww116_folder / "no_superchat").glob("*")]
    return has_superchats, no_superchats


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


@pytest.fixture(scope="function")
def video_with_file(test_ww_video_file):
    vid = VideoModel.create(
        youtube_id="asbsdrjgkdlsa;",
        title="test",
        episode="",
        upload_date="2020-01-01",
        duration=8531,
        description="this is a test",
        enabled=True,
        private=False,
    )
    FileManager.add_path_to_video(path=test_ww_video_file, video=vid)
    return vid


@pytest.fixture(scope="function")
def superchat(video_with_file) -> SuperchatModel:
    sc = SuperchatModel(
        frame_number=15,
        video_id=video_with_file.id,
    )
    sc.save()
    return sc


@pytest.fixture(scope="function")
def superchat_image_file(test_files):
    sc_file = [x for x in test_files.glob("*.jpg") if x.stem == "superchat"][0]
    return sc_file


@pytest.fixture(scope="function")
def superchat_image_array():
    img = Image.new("RGB", (100, 100), color="red")
    img = np.array(img)
    return img


@pytest.fixture(scope="function")
def superchat_with_file(video_with_file, superchat_image_file) -> SuperchatItem:
    sc_file = superchat_image_file
    sc = SuperchatModel.create(
        frame_number=0,
        video_id=video_with_file.id,
    )
    sci = SuperchatItem.from_model(sc)
    sci.add_image(sc_file)
    return sc


@pytest.fixture(scope="function")
def superchat_segment1(video):
    ss = SuperchatSegmentModel.create(start_time=0, end_time=10, video=video)
    return ss


@pytest.fixture(scope="function")
def superchat_segment2(video):
    ss = SuperchatSegmentModel.create(start_time=18, end_time=30, video=video)
    return ss
