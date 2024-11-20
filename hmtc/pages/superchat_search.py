from loguru import logger
import solara
from pathlib import Path
from dataclasses import dataclass
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.super_chat_ripper import SuperChatRipper
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem
from hmtc.models import Video as VideoModel
import numpy as np


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/videos")
    elif len(router.parts) == 2:

        return router.parts[level:][0], 0
    else:
        return router.parts[level:][0], int(router.parts[level:][1])


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
            logger.debug(f"MSE is too high to be the same")
            return False
    # shape is too different to be the same
    else:
        logger.debug(f"Shape is too different to be the same")
        logger.debug(f"Shape A: {imageA.shape}")
        logger.debug(f"Shape B: {imageB.shape}")
        return False


@solara.component
def SuperChatImageCard(superchat):
    with solara.Card():
        with solara.Row():
            solara.Image(superchat.image, width="80%")
        with solara.Row():
            solara.Text(f"Start Time: {superchat.start_time}")
            solara.Text(f"End Time: {superchat.end_time}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    MIN_SUPERCHAT_DURATION = 5
    current_superchat = None
    time_step = 5
    images_to_show = 5
    found_superchats = solara.use_reactive([])
    video_id, frame_number = parse_url_args()
    current_time = frame_number

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    vid_file = FileManager.get_file_for_video(video, "video")

    if vid_file.file_type == "":
        solara.Markdown(f"No video file found for video {video_id}")
    else:
        file_path = Path(vid_file.path) / vid_file.filename

        image_extractor = ImageExtractor(file_path)
        images = image_extractor.extract_frame_sequence(
            current_time, video.duration, time_step
        )

        for image in images:
            if len(found_superchats.value) >= images_to_show:
                break

            superchat_image, found = SuperChatRipper(image).find_superchat()

            if found:
                if current_superchat is None:
                    current_superchat = SuperChat(superchat_image, current_time)
                else:
                    sc = SuperChat(superchat_image, current_time)
                    logger.error(
                        f"Comparing {current_superchat.start_time} with {sc.start_time}"
                    )
                    the_same = are_the_same(current_superchat.image, sc.image)
                    if the_same:
                        # current superchat already in found_superchats
                        logger.debug("Found the same image. Moving on.")
                        current_time = current_time + time_step
                        continue

                    else:

                        # end the current superchat
                        current_superchat.end_time = current_time
                        if (
                            current_superchat.end_time - current_superchat.start_time
                            > MIN_SUPERCHAT_DURATION
                        ):
                            found_superchats.value.append(current_superchat)
                        current_superchat = sc
                        current_superchat = None

            else:
                logger.debug("No superchat found")
                if current_superchat is not None:
                    current_superchat.end_time = current_time
                    found_superchats.value.append(current_superchat)
                current_superchat = None
            current_time = current_time + time_step

        if found_superchats.value[-1].end_time is None:
            found_superchats.value[-1].end_time = current_time
        last_superchat = found_superchats.value[-1]
        with solara.Row():
            with solara.Link(
                f"/superchat-search/{video_id}/{last_superchat.end_time}",
            ):
                solara.Text(f"Next Page")

        for superchat in found_superchats.value:
            SuperChatImageCard(superchat)
