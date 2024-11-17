from pathlib import Path

import numpy as np
from PIL import Image
from loguru import logger
from hmtc.config import init_config
from hmtc.utils.opencv.image_editor import ImageEditor
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.super_chat_ripper import SuperChatRipper

config = init_config()
WORKING = Path(config["paths"]["working"])


TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_find_superchat_ww116_has_superchats(test_ww116_images):
    has_superchats, _ = test_ww116_images
    test_failed = False
    for image in has_superchats:
        tp = TARGET_PATH / "find_superchat" / "ww116" / "has_superchats"
        tp.mkdir(exist_ok=True, parents=True)

        # load example image from test folder
        editor = ImageEditor(image)
        if editor.image is None:
            raise ValueError("Image is None")

        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat(debug=True)
        if found:
            new_path = tp / "found"
            new_path.mkdir(exist_ok=True)
            new_superchat_filename = image.stem + "_superchat.jpg"
        else:
            test_failed = True
            new_path = tp / "not_found"
            new_path.mkdir(exist_ok=True)
            new_superchat_filename = image.stem + "_markup.jpg"
        new_file = new_path / new_superchat_filename
        # load image of superchat
        superchat = ImageEditor(sc_image)

        superchat.write_on_image(f"{str(image.stem)}")
        superchat.save_image(new_file)
        assert (new_file).exists()
        assert sc_image is not None
    assert not test_failed, "Missed a superchat where there shouldve been one"


def test_find_superchat_ww116_no_superchats(test_ww116_images):
    _, no_superchats = test_ww116_images
    test_failed = False
    for image in no_superchats:
        tp = TARGET_PATH / "find_superchat" / "ww116" / "no_superchats"
        tp.mkdir(exist_ok=True, parents=True)

        # load example image from test folder
        editor = ImageEditor(image)

        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat(debug=True)
        if found:
            test_failed = True
            new_path = tp / "found"
            new_path.mkdir(exist_ok=True)
            new_superchat_filename = image.stem + "_superchat.jpg"
        else:
            new_path = tp / "not_found"
            new_path.mkdir(exist_ok=True)
            new_superchat_filename = image.stem + "_markup.jpg"
        new_file = new_path / new_superchat_filename
        # load image of superchat
        superchat = ImageEditor(sc_image)

        superchat.write_on_image(f"{str(image.stem)}")
        superchat.save_image(new_file)
        assert (new_file).exists()
        assert sc_image is not None
    assert not test_failed, "Found a superchat where there shouldn't be one"
