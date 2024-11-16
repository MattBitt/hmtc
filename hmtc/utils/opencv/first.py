import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from skimage.color import rgb2gray

from hmtc.config import init_config

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


class ImageExtractor:
    def __init__(self, video_path, time_interval=1000):
        # not sure about the units of time_interval
        self.video_path = video_path
        self.output_folder = STORAGE / "images"
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True, exist_ok=True)

        self.time_interval = timedelta(seconds=time_interval)
        self.frame_count = 0

        # Open the video
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise Exception("Error: Could not open the video.")

    def grab_frame(self, timestamp):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = self.cap.read()
        return ret, frame

    def save_image(self, frame, image_filename):
        cv2.imwrite(self.output_folder / image_filename, frame)

    def split_video_to_images_with_timestamps(self):
        current_frame = 0
        while True:
            ret, frame = self.cap.read()

            if not ret:
                break
            if current_frame % self.time_interval.total_seconds() == 0:
                image_filename = (
                    f"{self.output_folder}/frame_{self.frame_count:04d}.jpg"
                )
                self._add_timestamp_to_frame(frame)
                self.save_image(frame, image_filename)
            current_frame += 1
            self.frame_count += 1

    def _add_timestamp_to_frame(self, frame):
        timestamp = self.start_time + self.frame_count * self.time_interval
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame, timestamp_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    def release_video(self):
        self.cap.release()

    @property
    def current_time(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000


def find_superchat(image) -> tuple:

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

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

    if max_contour is not None:
        # Return the section bounded by the largest contour
        x, y, w, h = cv2.boundingRect(max_contour)
        return cv2.cvtColor(hsv[y : y + h, x : x + w], cv2.COLOR_HSV2BGR), (x, y, w, h)

    return None


def images_are_the_same(img1, img2):
    if img1.shape != img2.shape:
        h1, w1, _ = img1.shape
        h2, w2, _ = img2.shape
        if abs(h1 - h2) / h1 > 0.1 or abs(w1 - w2) / w1 > 0.1:
            # more than 10 percent difference in size
            return False
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    im1_weighted_mean = rgb2gray(img1)
    im2_weighted_mean = rgb2gray(img2)
    similarity = np.sum((im1_weighted_mean - im2_weighted_mean) ** 2)
    if similarity < 10000:
        return True
    return False


def get_region_of_interest(image, rectangle):
    x, y, w, h = rectangle
    return image[y : y + h, x : x + w]


def capture_superchats(video_path):
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
        ret, frame = ie.grab_frame(current_frame)
        if not ret:
            break

        processed_frames += 1
        superchat, rectangle = find_superchat(frame)
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


if __name__ == "__main__":
    video_path = "hmtc/utils/opencv/working_video.mp4"
    start = time.time()
    superchats = capture_superchats(video_path)
    end = time.time()
    logger.error(f"Time taken: {end - start:.2f} seconds to capture superchats")
    for s in superchats:
        cv2.imwrite(STORAGE / f"images/superchat_{s[1]}_{s[2]}.jpg", s[0])

    logger.error(f"Found {len(superchats)} superchats")
