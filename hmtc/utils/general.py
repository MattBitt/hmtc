import os
import re
from loguru import logger
import csv
from pathlib import Path
from datetime import datetime


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def parse_video_file_name(file):
    # this is for finding existing information
    # about files already downloaded.
    # dont want to redownload 200+ GB, again.
    pattern = r"(\d{4}-\d{2}-\d{2})_([a-z-]+)_([a-z0-9_.-]+)_([a-zA-Z0-9_.-]{11})_(\d{3,4}p-[a-z0-9-]+)"

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


def my_move_file(source, target):

    s = Path(source)
    t = Path(target)
    result = s.rename(t)
    return result

    # except Exception as e:
    #     logger.error(f"Error moving file: {e}")
    #     return ""


def rename_files():

    for file in Path(
        "/mnt/c/DATA/hmtcasdf_files/previous/harry_mack/video/livestreams/"
    ).glob("*.*"):
        video_info = parse_video_file_name(file)
        if video_info:
            new_name = f"{video_info['upload_date']}___{video_info['youtube_id']}"
            new_name = new_name + file.suffix
            new_path = (
                Path(
                    f"/mnt/c/DATA/hmtcfdsa_files/media/{video_info['upload_date'][0:4]}"
                )
                / new_name
            )
            logger.debug(f"Renaming {file} to {new_path}")
            my_move_file(file, new_path)
        else:
            logger.debug(f"Skipping {file}")


def get_youtube_id(filename):
    pattern = r"^.*___([a-zA-Z0-9_.-]{11}).*"
    f = Path(filename)
    try:
        match = re.match(pattern, f.stem).group(1)
        return match
    except AttributeError:
        logger.error(f"Could not find youtube id in {f}")
        return None


def is_disk_full(path):
    disk = os.statvfs(path)
    free_space = disk.f_bavail * disk.f_frsize
    GIGABYTE = 1024 * 1024 * 1024
    MIN_FREE_SPACE = 20  # GB
    if free_space < MIN_FREE_SPACE * GIGABYTE:
        return True
    return False


def time_since_update(playlist):
    if not playlist.last_update_completed:
        return "Never"

    t = datetime.now() - playlist.last_update_completed

    if t.seconds > (24 * 3600):
        return str(f"{t.days} days ago")
    elif t.seconds > 3600:
        return str(f"{t.seconds // 3600} hours ago")
    elif t.seconds < 3600 and t.seconds > 60:
        return str(f"{(t.seconds // 60)} minutes ago")
    else:
        return str("Just now")
