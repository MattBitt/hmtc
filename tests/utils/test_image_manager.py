from pathlib import Path

from hmtc.config import init_config
from hmtc.utils.opencv.image_manager import ImageManager

config = init_config()

WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

INPUT_PATH = WORKING / "files_for_input"
OUTPUT_PATH = WORKING / "files_created_by_testing"


def test_image_mangager_path(test_image_filename):
    editor = ImageManager(test_image_filename)
    assert editor.image_path.exists()
    assert editor.image_path == test_image_filename


def test_image_mangager_string(test_image_filename):
    path_string = str(test_image_filename)
    editor = ImageManager(str(path_string))
    assert editor.image_path.exists()
    assert editor.image_path == test_image_filename


def test_write_on_image(test_image_filename):
    output_folder = OUTPUT_PATH / "write_on_image"
    output_folder.mkdir(exist_ok=True)
    editor = ImageManager(test_image_filename)
    assert editor.image_path.exists()
    editor.write_on_image("Test Text")

    new_image = output_folder / f"a_random_image_markedup.jpg"
    editor.save_image(new_image)
