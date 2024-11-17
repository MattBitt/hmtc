import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from loguru import logger
from PIL import Image
from skimage.color import rgb2gray
from hmtc.utils.opencv.image_tools import images_are_the_same, get_region_of_interest
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.config import init_config

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])
MINIMUM_AREA = 10000


class SuperChatRipper:
    def __init__(self, image):
        self.image = image

    def find_superchat(self) -> Optional[np.ndarray]:

        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        # Define color range for bright colors (adjust as needed)
        lower_bright = np.array([0, 100, 100])
        upper_bright = np.array([179, 255, 255])

        # Create a mask for bright colors
        mask = cv2.inRange(hsv, lower_bright, upper_bright)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_contour = None

        # Find the largest contour (brightest color box)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                max_contour = contour

        if max_contour is not None and max_area > MINIMUM_AREA:
            # Return the section bounded by the largest contour
            x, y, w, h = cv2.boundingRect(max_contour)
            return cv2.cvtColor(hsv[y : y + h, x : x + w], cv2.COLOR_HSV2BGR)
        else:
            logger.debug(f"Cound not find superchat")
            logger.debug(f"Contour OR: {max_contour}")
            logger.debug(f"Area too small: {max_area}")
            return None


def capture_superchats(self, video_path):
    PROCESS_FRAME_N_SECONDS = 30000
    MINIMUM_SUPERCHAT_LENGTH = 20
    SUPERCHAT_LIMIT = 300

    ie = ImageExtractor(video_path)
    if ie is None:
        logger.error("Could not create ImageExtractor")
        return

    length = int(ie.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = length / ie.cap.get(cv2.CAP_PROP_FPS)  # 60 frames per second

    superchats = []
    current_superchat = None

    start_time = None
    end_time = None
    current_frame = 0
    compare_counter = 0
    processed_frames = 0

    while len(superchats) < SUPERCHAT_LIMIT:
        frame = ie.grab_frame(current_frame)
        processed_frames += 1
        superchat, rectangle = self.find_superchat(frame)
        if superchat is not None:
            if current_superchat is None:
                start_time = ie.current_time
                current_superchat = superchat
            else:
                capture = get_region_of_interest(frame, rectangle)
                if images_are_the_same(img1=current_superchat, img2=capture):
                    compare_counter += 1
                    current_frame += PROCESS_FRAME_N_SECONDS
                    continue

                else:
                    end_time = ie.current_time
                    if end_time - start_time > MINIMUM_SUPERCHAT_LENGTH:
                        superchats.append((current_superchat, start_time, end_time))
                    current_superchat = superchat
                    start_time = ie.current_time
        current_frame += PROCESS_FRAME_N_SECONDS
    logger.debug(f"Length: {length}")
    logger.debug(f"Duration: {duration}")
    logger.debug(f"Processed frames: {processed_frames}")
    logger.debug(f"Compare counter: {compare_counter} / {current_frame}")
    ie.release_video()
    return superchats
