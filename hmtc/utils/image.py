from pathlib import Path

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
