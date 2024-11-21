from loguru import logger
import solara
from pathlib import Path
from dataclasses import dataclass
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.super_chat_ripper import SuperChatRipper
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem
from hmtc.models import Video as VideoModel
import numpy as np
import random
import cv2
import time


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


def filter1(orig_image):
    image = orig_image.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for bright colors (adjust as needed)
    lower_bright = np.array([0, 100, 100])
    upper_bright = np.array([179, 255, 255])

    # Create a mask for bright colors
    mask = cv2.inRange(hsv, lower_bright, upper_bright)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and keep the 5 largest
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])

    # Draw the largest 3 contours on the image
    for contour in contours[:3]:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return image


def filter2(orig_image):
    image = orig_image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return None, False

    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    return image


def filter3(image):
    return cv2.GaussianBlur(image, (15, 15), 0)


def filter4(image):
    return cv2.GaussianBlur(image, (1, 1), 0)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    video_id = parse_url_args()

    if video_id is None or video_id == 0:
        raise ValueError(f"No Video Found {video_id}")

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    video_file = FileManager.get_file_for_video(video, filetype="video")
    if video_file is None:
        raise ValueError(f"No File Found {video.file_id}")
    file_path = Path(video_file.path) / video_file.filename

    image_extractor = ImageExtractor(file_path)
    # frame_number = solara.use_reactive(random.randint(0, image_extractor.frame_count))
    frame_number = random.randint(0, image_extractor.frame_count)
    image = image_extractor.grab_frame(frame_number)

    frame_number = random.randint(0, image_extractor.frame_count)
    image2 = image_extractor.grab_frame(frame_number)

    frame_number = random.randint(0, image_extractor.frame_count)
    image3 = image_extractor.grab_frame(frame_number)

    frame_number = random.randint(0, image_extractor.frame_count)
    image4 = image_extractor.grab_frame(frame_number)
    start_time = time.time()
    filtered1 = filter1(image)
    logger.debug(f"Filter 1 Time: {time.time() - start_time} ms")
    start_time = time.time()
    filtered2 = filter1(image2)
    logger.debug(f"Filter 2 Time: {time.time() - start_time}")
    start_time = time.time()
    filtered3 = filter1(image3)
    logger.debug(f"Filter 3 Time: {time.time() - start_time}")
    start_time = time.time()
    filtered4 = filter1(image4)
    logger.debug(f"Filter 4 Time: {time.time() - start_time}")
    with solara.Row(justify="center"):
        solara.Text(f"Frame Number: {416263}")
        solara.Image(image, width="600px")
    with solara.Row(justify="center"):
        solara.Image(filtered1, width="100%")
        solara.Image(filtered2, width="100%")
    with solara.Row(justify="center"):
        solara.Image(filtered3, width="100%")
        solara.Image(filtered4, width="100%")
