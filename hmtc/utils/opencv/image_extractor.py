import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
from loguru import logger
from numpy.typing import NDArray

from hmtc.config import init_config

config = init_config()
WORKING = Path(config["WORKING"])
STORAGE = Path(config["STORAGE"])


def setup_output_folder():
    output_folder = STORAGE / "superchats"
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)
        output_folder.mkdir()
    return output_folder


class ImageExtractor:
    def __init__(self, input_video_path: Path, output_path: Path = None):
        self.video_path = input_video_path
        if not self.video_path.exists():
            raise Exception(f"Error: Video file does not exist. {input_video_path}")
        self.output_folder = output_path
        if output_path is not None:
            if not self.output_folder.exists():
                raise Exception("Error: Output folder does not exist.")

        # Open the video
        self.cap = cv2.VideoCapture(input_video_path)

        if not self.cap.isOpened():
            raise Exception("Error: Could not open the video.")

    def extract_frame(self, seconds: int):
        frame = seconds * self.fps
        frame = self.grab_frame(frame)
        return frame

    def extract_frame_sequence(self, start_time, end_time, interval):
        for timestamp in range(start_time, end_time, interval):
            frame = timestamp * self.fps
            frame = self.grab_frame(frame)
            logger.error(f"Extracted frame at {timestamp}")
            yield frame

    def grab_frame(self, frame) -> NDArray:
        if frame < 0:
            logger.error("Frame_number cannot be negative")
            raise ValueError(f"Frame_number cannot be negative {frame}")
        if frame > self.frame_count:
            logger.error("Frame_number cannot be greater than frame count")
            raise ValueError(
                f"Frame_number cannot exceed frame count {frame} / {self.frame_count}"
            )

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ret, frame = self.cap.read()
        if not ret:
            logger.error(f"Could not read frame at frame {frame}")
            raise Exception(f"Could not read frame at frame {frame}")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def save_image(self, image_filename, frame):
        if self.output_folder is None:
            logger.error("No output folder specified")
            raise Exception("No output folder specified in ImageExtractor save_image")
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
        frames_to_grab = self.frame_count // (num_seconds * self.fps) - 1
        logger.debug(f"About to grab a frame every {num_seconds} seconds")
        logger.debug(f"Total frames to grab: {frames_to_grab}")
        for _ in range(frames_to_grab):
            timestamp += self.fps * num_seconds
            frame = self.grab_frame(timestamp)
            yield frame

    @property
    def current_time(self):
        # returns time in seconds
        return int(self.cap.get(cv2.CAP_PROP_POS_MSEC) / self.fps)

    @property
    def frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def fps(self):
        return int(self.cap.get(cv2.CAP_PROP_FPS))
