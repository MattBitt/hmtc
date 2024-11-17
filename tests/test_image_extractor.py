from pathlib import Path

from hmtc.config import init_config
from hmtc.utils.opencv.image_extractor import ImageExtractor

config = init_config()
WORKING = Path(config["paths"]["working"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_extract_image(test_ww_video_file):
    assert test_ww_video_file.exists()


def test_basic_image_extractor(test_ww_video_file):
    assert test_ww_video_file.exists()
    ie = ImageExtractor(test_ww_video_file, TARGET_PATH)
    assert ie.output_folder.exists()
    assert ie.output_folder.is_dir()
    assert ie.cap.isOpened()

    assert ie.current_time == 0.0
    frame = ie.grab_frame(1000)

    assert frame is not None
    assert ie.current_time == 1
    ie.save_image("test_image.jpg", frame)
    assert (ie.output_folder / "test_image.jpg").exists()
    frame = ie.grab_frame(1000 * 60 * 5)  # some out of bounds time
    assert frame is None
    ie.release_video()
    assert not ie.cap.isOpened()


def test_save_n_records(test_ww_video_file):
    tp = TARGET_PATH / "save_n_records"
    tp.mkdir(exist_ok=True)
    ie = ImageExtractor(test_ww_video_file, tp)
    ie.save_n_random_frames(5)
