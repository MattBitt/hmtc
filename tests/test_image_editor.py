from pathlib import Path

from hmtc.config import init_config
from hmtc.utils.opencv.image_editor import ImageEditor

config = init_config()

WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

INPUT_PATH = WORKING / "files_for_input"
OUTPUT_PATH = WORKING / "files_created_by_testing"


def test_write_on_image(test_image_filename):
    output_folder = OUTPUT_PATH / "write_on_image"
    output_folder.mkdir(exist_ok=True)
    editor = ImageEditor(test_image_filename)
    assert editor.image_path.exists()
    editor.write_on_image("Test Text")

    new_image = output_folder / f"a_random_image_markedup.jpg"
    editor.save_image(new_image)
