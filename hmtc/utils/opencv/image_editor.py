import time
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image
from hmtc.config import init_config


config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

# Font settings
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (255, 255, 255)  # White color
font_thickness = 2

# Position to draw text
text_position = (10, 50)  # Top-left corner

# Draw the text on the image


class ImageEditor:
    def __init__(self, image):
        if isinstance(image, (str, Path)):
            self.image_path = Path(image)
            if not self.image_path.exists():
                raise Exception("Error: Could not open the image.")
            self.image = cv2.imread(str(self.image_path))
        elif isinstance(image, (np.ndarray, np.generic)):
            self.image = image
            self.image_path = None
        else:
            raise TypeError("Image must be a file path or a numpy array.")

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
        if path is None:
            if self.image_path is None:
                raise ValueError("No path provided to save the image.")
            path = self.image_path
        cv2.imwrite(str(path), self.image)
