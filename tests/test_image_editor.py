from hmtc.utils.opencv.image_editor import ImageEditor
from hmtc.config import init_config
from pathlib import Path

config = init_config()
WORKING = Path(config["paths"]["working"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_write_on_image(test_image_filename):
    new_image = TARGET_PATH / f"some_image_markup.jpg"
    editor = ImageEditor(test_image_filename)
    assert editor.image_path.exists()
    editor.write_on_image("Test Text")
    editor.save_image(new_image)


def test_write_on_ww_images(test_ww_images):
    for image in test_ww_images:
        new_image = TARGET_PATH / f"{str(image.stem)}_markup.jpg"
        editor = ImageEditor(image)
        editor.write_on_image(str(image))
        editor.save_image(new_image)
