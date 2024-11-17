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


def test_find_superchat(test_ww_images):

    for image in test_ww_images:
        tp = TARGET_PATH / "find_superchat"
        tp.mkdir(exist_ok=True)

        # load example image from test folder
        editor = ImageEditor(image)

        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat(debug=True)
        if found:
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
