from loguru import logger
import solara
from pathlib import Path
from dataclasses import dataclass
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.video import VideoItem
from hmtc.models import Video as VideoModel
import numpy as np


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
def SuperChatSearcher(video):
    MIN_SUPERCHAT_DURATION = 20
    TIME_STEP = 10
    IMAGES_TO_SHOW = 5

    found_superchats = []
    current_time = solara.use_reactive(0)
    current_superchat = None
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
        solara.Button("Next Page", on_click=lambda: load_next_page(current_time.value))
    for image in images.value:
        if len(found_superchats) >= IMAGES_TO_SHOW:
            break
        logger.error(f"Current Time: {current_time.value}")
        logger.error(f"Number of Superchats found  {len(found_superchats)}")
        superchat_image, found = SuperChatRipper(image).find_superchat()

        if found:
            if current_superchat is None:
                current_superchat = SuperchatItem(
                    image=superchat_image,
                    start_time=current_time.value,
                    video_id=video.id,
                )
            else:
                sc = SuperchatItem(
                    image=superchat_image,
                    start_time=current_time.value,
                    video_id=video.id,
                )
                logger.error(
                    f"Comparing {current_superchat.start_time} with {sc.start_time}"
                )
                the_same = are_the_same(current_superchat.image, sc.image)
                if the_same:
                    # current superchat already in found_superchats
                    logger.debug("Found the same image. Moving on.")
                    current_time.value = current_time.value + TIME_STEP
                    continue

                else:

                    # end the current superchat
                    current_superchat = current_superchat.update_end_time(
                        current_time.value
                    )
                    if (
                        current_superchat.end_time - current_superchat.start_time
                        > MIN_SUPERCHAT_DURATION
                    ):
                        found_superchats.append(current_superchat)
                    current_superchat = sc
                    current_superchat = None

        else:
            logger.debug("No superchat found")
            if current_superchat is not None:
                current_superchat = current_superchat.update_end_time(
                    current_time.value
                )
                if (
                    current_superchat.end_time - current_superchat.start_time
                    > MIN_SUPERCHAT_DURATION
                ):
                    found_superchats.append(current_superchat)
            current_superchat = None
        current_time.value = current_time.value + TIME_STEP
    if len(found_superchats) > 0:
        if found_superchats[-1].end_time is None:
            current_superchat = current_superchat.update_end_time(current_time.value)
        last_superchat = found_superchats[-1]

    for superchat in found_superchats:
        SuperChatImageCard(superchat)


@solara.component
def SuperChatImageCard(superchat):
    with solara.Card():
        with solara.Row():
            solara.Image(superchat.image, width="80%")
            with solara.Column():
                solara.Text(f"Start Time: {superchat.start_time}")
                solara.Text(f"End Time: {superchat.end_time}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    video_id = parse_url_args()

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))

    SuperChatSearcher(video)
