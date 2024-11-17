import numpy as np
from PIL import Image
from pathlib import Path
from hmtc.utils.opencv.super_chat_ripper import SuperChatRipper
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_editor import ImageEditor
from hmtc.config import init_config

config = init_config()
WORKING = Path(config["paths"]["working"])


TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_find_superchat(test_ww_images):

    for image in test_ww_images:
        new_image = TARGET_PATH / f"{str(image.stem)}_superchat.jpg"

        # load example image from test folder
        editor = ImageEditor(image)

        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image = sc.find_superchat()

        # load image of superchat
        superchat = ImageEditor(sc_image)

        superchat.draw_rectangle(20, 20, 100, 50)
        superchat.write_on_image("Superchat!!!")
        superchat.save_image(new_image)
        assert new_image.exists()
        assert sc_image is not None
