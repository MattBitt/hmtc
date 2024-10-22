import csv
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from loguru import logger


def clean_filename(dirty):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", dirty)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def parse_video_filename(file):
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


def my_copy_file(source, target):
    s = str(Path(source))
    t = str(Path(target))

    try:
        shutil.copy(s, t)
        logger.debug(f"Copying file {source} to {target}")
    except Exception as e:
        logger.error(f"Error copying file {source} to {target}: {e}")


def my_move_file(source, target):
    logger.debug(f"Moving file {source} to {target}")
    if source == target:
        return target

    s = Path(source)
    assert s.exists()
    t = Path(target)
    t.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(s, t)
    s.unlink()
    return t


def save_file_to_disk(source, target):
    with open(target, "wb") as f:
        f.write(source)
    return target


def get_youtube_id(filename):
    f = Path(filename)
    pattern = r"^.*___([a-zA-Z0-9_.-]{11}).*"

    try:
        match = re.match(pattern, f.stem).group(1)
        if match[-1] == ".":
            return match[:-1]

        return match

    except AttributeError:
        # logger.error(f"No valid youtube id found in {f}. Checking for bad video id")
        pattern = r"^.*___([a-zA-Z0-9_.-]{10}).*"
        try:
            match = re.match(pattern, f.stem).group(1)
            return match
        except AttributeError:
            logger.error(f"No invalid youtube id found in {f}")

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


def read_json_file(filename):
    if filename.exists():
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    else:
        logger.error(f"File {filename} does not exist")


def determine_file_object_association(file):
    file = Path(file)
    if file.name == "series_info.txt":
        return "series", {"dummy": "data"}
    elif file.suffix == ".json":
        data = read_json_file(file)
        if file.stem[:2] == "PL" and len(file.stem) > 33:
            p_id = file.stem[:34]
            return "playlist", data

        if "formats" in data:
            idstring = get_youtube_id(file)
            if len(idstring) == 10:
                return "bad video", {"id": idstring}

            if idstring not in file.stem:
                logger.error(f"Youtube id not in filename {file} {idstring}")
            return "video", {"id": idstring}

        if "uploader" in data and "channel" in data:
            return "channel", data

    else:
        if file.stem[:2] == "PL" and len(file.stem) > 33:
            p_id = file.stem[:34]
            return "playlist", {"id": p_id}

        idstring = get_youtube_id(file)
        if not idstring:
            return "unknown", {"dummy": "data"}
        if len(idstring) == 11:
            if idstring not in file.stem:
                logger.error(f"Youtube id not in filename {file} {idstring}")
            return "video", {"id": idstring}
        elif len(idstring) == 10:
            return "bad video", {"id": idstring}

        else:
            logger.debug(f"Unknown file type {file}")
            return "who knows", {"theshadow": "knows"}


def check_folder_exist_and_writable(folder: Path):
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(
            f"Folder {folder} does not exist or is not a directory. Please create it and try again."
        )

    test_file = folder / "asdf.txt"
    try:
        with open(test_file, "w") as f:
            f.write("asdf test asdf")
        with open(test_file, "r") as f:
            if f.read() != "asdf test asdf":
                raise FileNotFoundError(
                    f"Folder {folder} is not writable. Please fix and try again."
                )
    except FileNotFoundError as e:
        logger.error(e)
        raise
    finally:
        test_file.unlink()


def move_file(source: str, dest: str):
    d = Path(dest)

    if d.exists() and d.is_file():
        ## warning. I'm updating this on 9/29 to alway overwrite the destination
        # i've finished the initial sort, so anything i download now, should be
        # on purpose
        logger.debug(f"File {dest} already exists. Overwriting.")
        pass

    try:
        shutil.move(source, dest)
    except FileNotFoundError:
        logger.debug(f"source = {source} dest = {dest}")
    except PermissionError:
        logger.debug("Permission denied.")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def is_absolute(path: str) -> bool:
    return Path(path) == Path(path).resolve()
