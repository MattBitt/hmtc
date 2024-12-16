import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from loguru import logger
from PIL import Image

from hmtc.config import init_config
from hmtc.domains.superchat import Superchat as SuperchatItem
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

config = init_config()
WORKING = Path(config["WORKING"])


TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_find_superchat_ww116_has_superchats(test_ww116_images):
    has_superchats, _ = test_ww116_images
    test_failed = False
    for image in has_superchats:
        tp = TARGET_PATH / "find_superchat" / "ww116" / "has_superchats"
        tp.mkdir(exist_ok=True, parents=True)

        # load example image from test folder
        editor = ImageManager(image)
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
        superchat = ImageManager(sc_image)

        superchat.write_on_image(f"{str(image.stem)}")
        superchat.save_image(new_file)
        assert (new_file).exists()
        assert sc_image is not None
    assert not test_failed, "Missed a superchat where there shouldve been one"


@pytest.mark.xfail(reason="Need to tweak the superchat ripper to be more accurate")
def test_find_superchat_ww116_no_superchats(test_ww116_images):
    _, no_superchats = test_ww116_images
    test_failed = False
    for image in no_superchats:
        tp = TARGET_PATH / "find_superchat" / "ww116" / "no_superchats"
        tp.mkdir(exist_ok=True, parents=True)

        # load example image from test folder
        editor = ImageManager(image)

        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat(debug=True)
        if found:
            test_failed = True
            new_path = tp / "found"
            new_path.mkdir(exist_ok=True)
            new_superchat_filename = image.stem + "_markup.jpg"
            new_file = new_path / new_superchat_filename
            # load image of superchat
            superchat = ImageManager(sc_image)

            superchat.write_on_image(f"{str(image.stem)}")
            superchat.save_image(new_file)
            assert (new_file).exists()
            assert sc_image is not None
        else:
            test_failed = False

    assert not test_failed, "Found a superchat where there shouldn't be one"


def test_grab_superchats_from_video(test_ww_video_file):
    tp = TARGET_PATH / "grab_superchats_from_video"
    tp.mkdir(exist_ok=True)
    VIDEO_LENGTH = 60
    HOW_MANY_FRAMES = 6

    ie = ImageExtractor(test_ww_video_file, tp)

    for frame in ie.frame_each_n_seconds(VIDEO_LENGTH // HOW_MANY_FRAMES):
        assert frame is not None
        original_frame = ImageManager(frame)
        original_frame.save_image(tp / f"{ie.current_time}_original.jpg")
        sc = SuperChatRipper(frame)
        sc_image, found = sc.find_superchat(debug=False)

    ie.release_video()
    assert not ie.cap.isOpened()
    files = tp.glob("*")
    assert len(list(files)) == HOW_MANY_FRAMES - 1


@pytest.mark.skip(reason="This test is too slow. Just for benchmarking")
def test_image_as_file_speed(test_image_filename):
    tp = TARGET_PATH / "save_image_speed"
    tp.mkdir(exist_ok=True)
    editor = ImageManager(test_image_filename)
    start = time.time()
    for i in range(10):
        editor.save_image(tp / f"{i}.jpg")
    file_save_time = time.time() - start
    start = time.time()
    for i in range(10):
        editor = ImageManager(tp / f"{i}.jpg")
    file_load_time = time.time() - start


def test_superchat_model(video):

    sc = SuperchatModel(
        frame=0,
        video_id=video.id,
    )
    sc.save()


def test_superchat_item(superchat):
    tp = TARGET_PATH / "superchat_item"
    tp.mkdir(exist_ok=True)

    sci = SuperchatItem.from_model(superchat)
    assert sci.id == superchat.id


def test_superchat_item_with_file(superchat, superchat_image_file):
    tp = TARGET_PATH / "superchat_item_with_file"
    tp.mkdir(exist_ok=True)

    sci = SuperchatItem.from_model(superchat)
    sci.add_image(superchat_image_file)
    assert sci.id == superchat.id
    assert len(sci.files) == 1


def test_superchat_item_with_array(superchat, superchat_image_array):
    tp = TARGET_PATH / "superchat_item_with_array"
    tp.mkdir(exist_ok=True)

    sci = SuperchatItem.from_model(superchat)
    sci.add_image(superchat_image_array)
    assert sci.id == superchat.id

    assert len(sci.files) == 1


def test_ripper_to_item(video_with_file, test_ww116_images):
    video = video_with_file
    has_superchats, _ = test_ww116_images
    tp = TARGET_PATH / "ripper_to_item"
    tp.mkdir(exist_ok=True)

    counter = 0
    for image in has_superchats:
        editor = ImageManager(image)
        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat()
        assert found
        new_sc = SuperchatModel.create(frame=counter, video_id=video.id)
        superchat = SuperchatItem.from_model(new_sc)
        superchat.add_image(sc_image)
        assert superchat.get_image() is not None
        new_sc = SuperchatModel.get(frame=counter, video_id=video.id)
        assert new_sc is not None
        assert new_sc.video.id == video.id
        assert new_sc.frame == counter
        # sc_file_db = SuperchatFileModel.get_or_none(superchat_id=new_sc.id)
        # assert sc_file_db is not None
        img = superchat.get_image()
        assert isinstance(img, np.ndarray)
        counter = counter + 1
