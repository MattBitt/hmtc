import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from skimage.color import rgb2gray

from hmtc.config import init_config
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_tools import get_region_of_interest, images_are_the_same

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])
MINIMUM_AREA = 10000


class SuperChatRipper:
    def __init__(self, image: np.ndarray):
        if image is None:
            logger.error("Image is None")
            raise ValueError("Image is None")
        self.image = image

    def find_superchat(self, debug=False) -> tuple:

        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

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

        max_contour = None
        max_area = 0

        # Prioritize contours on the left side of the screen
        image_h, image_w, _ = self.image.shape
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if x < image_w / 2 and area > MINIMUM_AREA:
                max_contour = contour

        if max_contour is not None:
            x, y, w, h = cv2.boundingRect(max_contour)
            return cv2.cvtColor(hsv[y : y + h, x : x + w], cv2.COLOR_HSV2BGR), True

        else:
            if debug:
                markup = self.image.copy()
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(markup, (x, y), (x + w, y + h), (0, 255, 0), 2)
                return markup, False
            return None, False

    def grab_superchats_from_video(self, video_path: Path):
        ie = ImageExtractor(video_path)
        if ie is None:
            logger.error(f"Could not create ImageExtractor for video {video_path}")
            return

        for frame in ie.frame_each_n_seconds(5):
            sc_image, found = self.find_superchat(frame)
            if found:
                yield sc_image