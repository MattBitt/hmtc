import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from skimage.color import rgb2gray

from hmtc.assets.colors import Colors
from hmtc.config import init_config
from hmtc.utils.image import hex_to_rgb
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.image_tools import get_region_of_interest, images_are_the_same

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])
MINIMUM_AREA = 10000
MIN_WIDTH = 100
MIN_HEIGHT = 100


class SuperChatRipper:
    def __init__(self, image: np.ndarray):
        if image is None:
            logger.error("Image is None")
            raise ValueError("Image is None")
        self.image = image

    def find_superchat(self, debug=False) -> tuple:
        xs = self.image.shape[0]
        ys = self.image.shape[1] * 0.5
        image = self.image[0 : int(xs), 0 : int(ys)].copy()
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

        if debug:
            # return the image with a colored rectangle for debugging
            rect_color = hex_to_rgb(str(Colors.ERROR))
            x, y, w, h = cv2.boundingRect(contours[0])
            cv2.rectangle(image, (x, y), (x + w, y + h), rect_color, 8)

            return image, True
        # only return the superchat if it is large enough
        x, y, w, h = cv2.boundingRect(contours[0])
        return image[y : y + h, x : x + w], True

    def grab_superchats_from_video(self, video_path: Path):
        ie = ImageExtractor(video_path)
        if ie is None:
            logger.error(f"Could not create ImageExtractor for video {video_path}")
            return

        for frame in ie.frame_each_n_seconds(5):
            sc_image, found = self.find_superchat(frame)
            if found:
                yield sc_image
