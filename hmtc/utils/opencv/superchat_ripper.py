import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from hmtc.assets.colors import Colors
from hmtc.utils.image import hex_to_rgb
import cv2
import numpy as np
from loguru import logger
from PIL import Image
from skimage.color import rgb2gray

from hmtc.config import init_config
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.opencv.image_tools import get_region_of_interest, images_are_the_same
from hmtc.utils.opencv.image_manager import ImageManager

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
            rect_color = hex_to_rgb(str(Colors.ERROR))
            x, y, w, h = cv2.boundingRect(contours[0])
            cv2.rectangle(image, (x, y), (x + w, y + h), rect_color, 8)

            return image, True
        else:
            x, y, w, h = cv2.boundingRect(contours[0])
            return image[y : y + h, x : x + w], True

    def find_superchat_using_canny(self, debug=False) -> tuple:
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        if debug:
            img = ImageManager(edges)
            img.save_image("canny.jpg")
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

            cv2.line(self.image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        return self.image, True

    def grab_superchats_from_video(self, video_path: Path):
        ie = ImageExtractor(video_path)
        if ie is None:
            logger.error(f"Could not create ImageExtractor for video {video_path}")
            return

        for frame in ie.frame_each_n_seconds(5):
            sc_image, found = self.find_superchat(frame)
            if found:
                yield sc_image
