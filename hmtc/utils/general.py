import os
import re
from loguru import logger
from collections import defaultdict
import csv


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def parse_video_file_name(file):
    # this is for finding existing information
    # about files already downloaded.
    # dont want to redownload 200+ GB, again.
    pattern = (
        r"(\d{4}-\d{2}-\d{2})_([a-z-]+)_([a-z0-9_.-]+)_(.{11})_(\d{3,4}p-[a-z0-9-]+)"
    )

    match = re.match(pattern, file.stem)
    video_info = {}
    if match:
        video_info["upload_date"] = match.group(1)
        video_info["name"] = match.group(2)
        video_info["title"] = match.group(3)
        video_info["youtube_id"] = match.group(4)
        video_info["quality"] = match.group(5)
        return video_info
    else:
        logger.debug(f"No match found for file: {file}")
        return None


def csv_to_dict(filename):
    info = []
    with open(filename, "r", encoding="utf-8-sig") as f:
        csvFile = csv.DictReader(f)
        for line in csvFile:
            info.append(line)
    return info
