import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
from loguru import logger
from numpy.typing import NDArray

from hmtc.config import init_config

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


def setup_output_folder():
    output_folder = STORAGE / "superchats"
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)
        output_folder.mkdir()
    return output_folder


class ImageExtractor:
    def __init__(self, input_video_path: Path, output_path: Path):
        # not sure about the units of time_interval
        self.video_path = input_video_path

        self.output_folder = output_path
        if not self.output_folder.exists():
            raise Exception("Error: Output folder does not exist.")

        # Open the video
        self.cap = cv2.VideoCapture(input_video_path)

        if not self.cap.isOpened():
            raise Exception("Error: Could not open the video.")

    def grab_frame(self, timestamp) -> NDArray:
        if timestamp < 0:
            logger.error("Timestamp cannot be negative")
            return None
        if timestamp > self.frame_count:
            logger.error("Timestamp cannot be greater than frame count")
            return None
        self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        ret, frame = self.cap.read()
        if not ret:
            logger.error(f"Could not read frame at timestamp {timestamp}")
            return None
        return frame

    def save_image(self, image_filename, frame):
        cv2.imwrite(self.output_folder / image_filename, frame)

    def release_video(self):
        self.cap.release()

    def save_n_random_frames(self, n):
        for _ in range(n):
            timestamp = random.randint(0, self.frame_count)
            frame = self.grab_frame(timestamp)
            self.save_image(f"random__{timestamp}.jpg", frame)

    def frame_each_n_seconds(self, num_seconds):
        timestamp = 0
        frames_to_grab = self.frame_count // (num_seconds * 60)  # 60fps
        if frames_to_grab < 0 or frames_to_grab > self.frame_count:
            raise ValueError(f"Invalid number of frames to grab {frames_to_grab}")
        for _ in range(frames_to_grab):
            timestamp += 60 * num_seconds
            frame = self.grab_frame(timestamp)
            yield frame

    @property
    def current_time(self):
        # returns time in seconds
        return self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

    @property
    def frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
