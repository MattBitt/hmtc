import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from loguru import logger
from PIL import Image

from hmtc.config import init_config
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

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


def test_superchat_model():
    new_vid = VideoModel.create(
        title="Test Video",
        description="This is a test video",
        youtube_id="123456",
        upload_date="2021-01-01",
        duration=1200,
    )
    sc = SuperchatModel(
        frame_number=0,
        video_id=new_vid.id,
    )
    sc.save()


def test_superchat_item():
    tp = TARGET_PATH / "superchat_item"
    tp.mkdir(exist_ok=True)

    new_vid = VideoModel.create(
        title="Test Video",
        description="This is a test video",
        youtube_id="123456",
        upload_date="2021-01-01",
        duration=1200,
    )
    sci = SuperchatItem(
        frame_number=0,
        video=new_vid,
        image=ImageManager(np.zeros((100, 100, 3), dtype=np.uint8)),
    )
    sci.image.save_image(tp / "superchat_item.jpg")


def test_ripper_to_item(test_ww116_images, test_ww_video_file):
    has_superchats, _ = test_ww116_images
    tp = TARGET_PATH / "ripper_to_item"
    tp.mkdir(exist_ok=True)

    new_vid = VideoModel.create(
        title="Test Video",
        description="This is a test video",
        youtube_id="123456",
        upload_date="2021-01-01",
        duration=1200,
    )
    FileManager.add_path_to_video(path=test_ww_video_file, video=new_vid)
    counter = 0
    for image in has_superchats:
        editor = ImageManager(image)
        # rip out superchat (if any)
        sc = SuperChatRipper(editor.image)
        sc_image, found = sc.find_superchat()
        assert found
        superchat = SuperchatItem(
            frame_number=counter,
            video=new_vid,
            image=ImageManager(sc_image).image,
        )
        ImageManager(superchat.image).write_on_image("Mizzle Bizzle Foshizzle")
        superchat.save_to_db()
        superchat.write_image(tp / f"{image.stem}_superchat.jpg")

        new_sc = SuperchatModel.get(frame_number=counter, video_id=new_vid.id)
        assert new_sc is not None
        assert new_sc.video.id == new_vid.id
        assert new_sc.frame_number == counter
        sc_file_db = SuperchatFileModel.get_or_none(superchat_id=new_sc.id)
        assert sc_file_db is not None
        img = superchat.get_image()
        assert isinstance(img, np.ndarray)
        counter = counter + 1
