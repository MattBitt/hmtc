import random
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel
from hmtc.utils.image import hex_to_rgb
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()
    if len(router.parts) == 1:
        router.push("/api/videos")
    else:
        return router.parts[level:][0]


def get_half_image(image, x=0.5):
    xs = image.shape[0]
    ys = image.shape[1] * x
    return image[0 : int(xs), 0 : int(ys)].copy()


def filter1(orig_image):
    image = get_half_image(orig_image)
    image_h, image_w, _ = image.shape
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv, True
    # Define color range for bright colors (adjust as needed)
    lower_bright = np.array([0, 100, 100])
    upper_bright = np.array([179, 255, 255])

    # Create a mask for bright colors
    mask = cv2.inRange(hsv, lower_bright, upper_bright)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if len(contours) == 0:
        return image, False

    rect_color = hex_to_rgb(str(Colors.WARNING))
    x, y, w, h = cv2.boundingRect(contours[0])
    cv2.rectangle(image, (x, y), (x + w, y + h), rect_color, 8)

    return image, True


def filter2(orig_image):

    image = get_half_image(orig_image)
    # inverted = cv2.bitwise_not(image)
    image_h, image_w, _ = image.shape
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for bright colors (adjust as needed)
    lower_bright = np.array([0, 110, 100])
    upper_bright = np.array([179, 255, 255])

    # Create a mask for bright colors
    mask = cv2.inRange(hsv, lower_bright, upper_bright)
    mask_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return mask_image, True
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if len(contours) == 0:
        return image, False

    rect_color = hex_to_rgb(str(Colors.ERROR))
    x, y, w, h = cv2.boundingRect(contours[0])
    cv2.rectangle(image, (x, y), (x + w, y + h), rect_color, 8)

    return image, True


def filter3(orig_image):
    image = get_half_image(orig_image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for bright colors (adjust as needed)
    lower_bright = np.array([0, 110, 100])
    upper_bright = np.array([179, 255, 255])

    # Create a mask for bright colors
    mask = cv2.inRange(hsv, lower_bright, upper_bright)
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if len(contours) == 0:
        return image, False

    rect_color = hex_to_rgb(str(Colors.ERROR))
    x, y, w, h = cv2.boundingRect(contours[0])
    cv2.rectangle(image, (x, y), (x + w, y + h), rect_color, 8)

    return image, True


def run_filters(image):
    image1, _ = filter1(image)
    image2, _ = filter2(image)
    image3, _ = filter3(image)
    return image1, image2, image3


@solara.component
def ImageCard(video):
    frame = solara.use_reactive(0)
    vid_file = FileManager.get_file_for_video(video, "video")

    if vid_file.file_type == "":
        solara.Markdown(f"No video file found for video {video.title}")
        return None

    file_path = Path(vid_file.path) / vid_file.filename

    image_extractor = ImageExtractor(file_path)
    image = image_extractor.extract_frame(frame.value)
    # images below are for video 2041 (ww116)
    # image = image_extractor.extract_frame(5569) # green
    # image = image_extractor.extract_frame(4033) # yellow
    # image = image_extractor.extract_frame(1940) # two superchats in one frame

    # images below are for video 355 (ww92)
    # image = image_extractor.extract_frame(823)  # green, but 2 separate superchats
    # image = image_extractor.extract_frame(180)  #
    # image = image_extractor.extract_frame(6750)  #
    a, b, c = run_filters(image)

    def randomize_frames():
        frame.set(random.randint(0, video.duration))

    with solara.Card():
        with solara.Row():

            solara.Text(f"Frame: {frame.value}")
            solara.Button("Random", on_click=randomize_frames)
            solara.Image(image=image, width="600px")

    with solara.Card():
        with solara.Columns([4, 4, 4]):
            solara.Image(image=a, width="380px")
            solara.Image(image=b, width="380px")
            solara.Image(image=c, width="380px")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    video_id = parse_url_args()

    if video_id is None:
        raise ValueError("No video ID provided")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    with solara.Row(justify="center"):
        ImageCard(video=video)
