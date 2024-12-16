import os
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
WORKING = Path(config["WORKING"])
STORAGE = Path(config["STORAGE"])


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
