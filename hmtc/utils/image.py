from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def convert_webp_to_png(file, path=None) -> Path:
    im = Image.open(file).convert("RGB")
    if path is None:
        new_file = Path(file.parent / (file.stem + ".png"))
    else:
        new_file = Path(path) / (file.stem + ".png")
    im.save(new_file, "png")
    return new_file


def convert_jpg_to_png(file):
    new_file = ""
    return new_file


def hex_to_rgb(hex_color):
    """Converts a hex color code to BGR format."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def are_images_similar(image1, image2):
    if (
        image1.shape[0] < 0.9 * image2.shape[0]
        or image1.shape[0] > 1.1 * image2.shape[0]
    ):
        return False
    if (
        image1.shape[1] < 0.9 * image2.shape[1]
        or image1.shape[1] > 1.1 * image2.shape[1]
    ):
        return False

    if image1.shape != image2.shape:
        if image1.shape[0] * image1.shape[1] > image2.shape[0] * image2.shape[1]:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        else:
            image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))

    def mse(imageA, imageB):
        # Compute the mean squared error between the two images
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    # Calculate the mean squared error and determine if images are similar
    mse_value = mse(image1, image2)
    threshold = 1500  # You can adjust this threshold value
    return mse_value < threshold
