from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.config import init_config
from pathlib import Path

config = init_config()
WORKING = Path(config["paths"]["working"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_extract_image(test_ww_video_file):
    assert test_ww_video_file.exists()


def test_basic_image_extractor(test_ww_video_file):
    assert test_ww_video_file.exists()
    output_file = TARGET_PATH
    ie = ImageExtractor(test_ww_video_file, output_file)
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
