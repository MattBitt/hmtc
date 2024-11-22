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


def hex_to_rgb(hex_color):
    """Converts a hex color code to BGR format."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
