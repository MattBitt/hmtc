import os
from pathlib import Path

import cv2
from loguru import logger

from hmtc.config import init_config

config = init_config()

WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


# Function to extract frames from a video until reaching the desired frame count
def extract_frames(video_file, folder_name, frame_count=150):
    cap = cv2.VideoCapture(video_file.get().file_string)

    frame_count = 0

    # Create an output folder with a name corresponding to the video
    output_directory = STORAGE / folder_name
    os.makedirs(output_directory, exist_ok=True)
    files = []
    while True:
        ret, frame = cap.read()
        # logger.debug(f"Ret: {ret}")
        # logger.debug(f"Frame: {frame}")
        # logger.debug(f"Frame {frame_count} read")
        # logger.debug(f"CAP_PROP_FPS: {cv2.CAP_PROP_FPS}")
        if not ret:
            break

        frame_count += 1

        # Only extract frames at the desired frame rate
        # 150 frames = 5 seconds
        if frame_count % 150 == 0:
            output_file = output_directory / f"frame_{frame_count}.jpg"
            files.append(output_file)
            cv2.imwrite(output_file, frame)
            logger.debug(
                f"Frame {frame_count} has been extracted and saved as {output_file}"
            )

    cap.release()
    return files


if __name__ == "__main__":
    video_file = r"static/omegle.webm"

    extract_frames(video_file, "asdf", 150)
