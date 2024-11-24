import time
from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from numpy.typing import NDArray
from PIL import Image

from hmtc.config import init_config
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.schemas.file import File as FileItem

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

# Font settings
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (255, 255, 255)  # White color
font_thickness = 4

# Position to draw text
text_position = (100, 100)


class ImageManager:
    def __init__(self, image):
        if isinstance(image, (str, Path)):
            self.image_path = Path(image)
            if not self.image_path.exists():
                raise Exception(f"Error: Could not open the image. {image}")
            self.image = cv2.imread(str(self.image_path), cv2.IMREAD_UNCHANGED)

        elif isinstance(image, FileItem):
            self.image_path = Path(image.path) / image.filename

            if not self.image_path.exists():
                raise Exception(f"Error: Could not open the image. {image}")

            self.image = cv2.imread(str(self.image_path), cv2.IMREAD_UNCHANGED)

            if self.image_path.suffix == ".webp":
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        elif isinstance(image, SuperchatFileModel):
            self.image_path = Path(image.path) / image.filename

            if not self.image_path.exists():
                raise Exception(f"Error: Could not open the image. {image}")

            self.image = cv2.imread(str(self.image_path), cv2.IMREAD_UNCHANGED)

            if self.image_path.suffix == ".webp":
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        elif isinstance(image, (np.ndarray, np.generic)):
            self.image = image
            self.image_path = None
        else:
            raise TypeError(
                f"Image must be a file path or a numpy array. Got {type(image)}"
            )

    def write_on_image(self, text):
        return cv2.putText(
            self.image,
            text,
            text_position,
            font,
            font_scale,
            font_color,
            font_thickness,
        )

    def draw_rectangle(self, x, y, w, h):
        self.image = cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def save_image(self, path=None):
        if self.image is None:
            raise ValueError("No image to save.")
        if path is None:
            if self.image_path is None:
                raise ValueError("No path provided to save the image.")
            path = self.image_path
        cv2.imwrite(str(path), self.image)
