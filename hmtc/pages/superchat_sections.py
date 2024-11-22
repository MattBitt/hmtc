from dataclasses import dataclass
from pathlib import Path

import numpy as np
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]


@dataclass
class SuperChat:
    image: np.ndarray
    start_time: float
    end_time: float = None


def mse(imageA, imageB):
    imgB = imageB.copy()
    if imageA.shape != imageB.shape:
        imgB.resize(imageA.shape)
    err = np.sum((imageA.astype("float") - imgB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err


def are_the_same(imageA, imageB):
    TOL = 0.2  # size tolerance
    MSE_TOL = 6000
    h1, w1, _ = imageA.shape
    h2, w2, _ = imageB.shape
    if abs(h1 - h2) / h1 < TOL and abs(w1 - w2) / w1 < TOL:
        the_mse = mse(imageA, imageB)
        logger.debug(f"MSE: {the_mse}")
        if the_mse < MSE_TOL:
            # same image?
            return True
        else:
            # logger.debug(f"MSE is too high to be the same")
            return False
    # shape is too different to be the same
    else:
        # logger.debug(f"Shape is too different to be the same")
        # logger.debug(f"Shape A: {imageA.shape}")
        # logger.debug(f"Shape B: {imageB.shape}")
        return False


@solara.component
def SuperChatSearcher(video, current_time):
    MIN_SUPERCHAT_DURATION = 20
    TIME_STEP = 10
    IMAGES_TO_SHOW = 200

    found_superchats = []

    images = solara.use_reactive([])

    def load_next_page(new_time):
        current_time.set(new_time)
        images.set(
            image_extractor.extract_frame_sequence(
                current_time.value, video.duration, TIME_STEP
            )
        )

    vid_file = FileManager.get_file_for_video(video, "video")

    if vid_file.file_type == "":
        solara.Markdown(f"No video file found for video {video.title}")
        return None

    file_path = Path(vid_file.path) / vid_file.filename

    image_extractor = ImageExtractor(file_path)
    with solara.Row():
        solara.Button(
            "Search For More Superchats!!!",
            on_click=lambda: load_next_page(current_time.value),
        )
    for image in images.value:
        if len(found_superchats) >= IMAGES_TO_SHOW:
            break
        logger.error(f"Current Time: {current_time.value}")
        logger.error(f"Number of Superchats found  {len(found_superchats)}")
        superchat_image, found = SuperChatRipper(image).find_superchat()

        if found:
            sci = ImageManager(superchat_image)
            sc = SuperchatItem(
                image=sci.image,
                frame_number=current_time.value,
                video=video,
            )
            sc.save_to_db()
            sc.write_image(filename=f"{current_time.value}.jpg")
            found_superchats.append(sc)
        current_time.value = current_time.value + TIME_STEP

    for superchat in found_superchats:
        SuperChatImageCard(superchat)


@solara.component
def SuperChatImageCard(superchat):
    img = superchat.get_image()
    if img is None:
        raise ValueError("No image found for superchat")
    with solara.Card():
        with solara.Row():
            solara.Image(img, width="80%")
            with solara.Column():
                solara.Text(f"Start Time: {superchat.frame_number}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    current_page = solara.use_reactive(1)
    video_id = parse_url_args()

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    existing_superchats = (
        SuperchatModel.select()
        .where(SuperchatModel.video_id == video.id)
        .order_by(SuperchatModel.frame_number.asc())
    ).paginate(current_page.value, 10)

    superchats = [
        SuperchatItem(frame_number=sc.frame_number).from_model(superchat=sc)
        for sc in existing_superchats
    ]
    if len(superchats) > 0:
        current_time = solara.use_reactive(superchats[-1].frame_number)
    else:
        current_time = solara.use_reactive(0)
    with solara.Row():
        solara.Button(
            "Previous Page",
            on_click=lambda: current_page.set(current_page.value - 1),
            disabled=current_page.value == 1,
        )
        solara.Text(f"Current Page: {current_page.value} Time {current_time.value}")
        solara.Button(
            "Next Page",
            on_click=lambda: current_page.set(current_page.value + 1),
        )

    # working pretty well, but if i search for superchats in the video,
    # and then click 'next page' it will search for superchats again and again
    # until i kill it

    for sc in superchats:
        SuperChatImageCard(sc)

    SuperChatSearcher(video, current_time=current_time)
