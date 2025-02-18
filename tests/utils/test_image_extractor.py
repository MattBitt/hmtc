from pathlib import Path

import pytest
from loguru import logger

from hmtc.config import init_config
from hmtc.utils.opencv.image_extractor import ImageExtractor

config = init_config()
WORKING = Path(config["WORKING"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


@pytest.mark.skip(reason="Need to rework the video fixture")
def test_extract_image(test_ww_video_file):
    assert test_ww_video_file.exists()


@pytest.mark.skip(reason="Need to rework the video fixture")
def test_save_n_records(test_ww_video_file):
    tp = TARGET_PATH / "save_n_records"
    tp.mkdir(exist_ok=True)
    ie = ImageExtractor(test_ww_video_file, tp)
    ie.save_n_random_frames(5)
    ie.release_video()
    assert not ie.cap.isOpened()


@pytest.mark.skip(reason="Need to rework the video fixture")
def test_basic_image_extractor(test_ww_video_file):
    assert test_ww_video_file.exists()
    ie = ImageExtractor(test_ww_video_file, TARGET_PATH)
    assert ie.output_folder.exists()
    assert ie.output_folder.is_dir()
    assert ie.cap.isOpened()

    assert ie.current_time == 0.0
    frame = ie.extract_frame(30)

    assert frame is not None
    assert ie.current_time == 500  # not sure why this is 500
    ie.save_image("test_image.jpg", frame)
    assert (ie.output_folder / "test_image.jpg").exists()
    ie.release_video()
    assert not ie.cap.isOpened()


@pytest.mark.skip(reason="Need to rework the video fixture")
def test_extract_frame_each_n_seconds(test_ww_video_file):

    tp = TARGET_PATH / "extract_frame_each_n_seconds"
    tp.mkdir(exist_ok=True)
    ie = ImageExtractor(test_ww_video_file, tp)
    counter = 0
    for _ in ie.frame_each_n_seconds(5):
        counter += 1
    assert counter == 11  # ignoring last frame
    counter = 0
    for _ in ie.frame_each_n_seconds(10):
        counter += 1
    assert counter == 5
    ie.release_video()
    assert not ie.cap.isOpened()
