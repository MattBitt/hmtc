import os
import subprocess
from pathlib import Path

import yt_dlp
from loguru import logger

# this is here only to run this file from the command line

# from hmtc.utils.general import is_disk_full


def is_disk_full(folder):
    return False


######


# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def internal_hook(d, *args, **kwargs):
    # if d["status"] == "downloading":
    #     logger.error(f"Downloading {d['downloaded_bytes']}")
    # if d["status"] == "finished":
    #     logger.error(f"Done downloading, now post-processing ...")
    pass


class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# this seems to work for playlists and channels
# if you send a channel it will grab all of the playlists
# if you send a playlist it will grab all of the videos
def fetch_ids_from(url, download_path="."):
    # couldn't figure out how to get this list without saving it to disk first ...
    downloaded_file = Path(download_path) / "ids.txt"
    cmd = f"yt-dlp --flat-playlist --print-to-file id {str(downloaded_file)} {url}".split()
    yt_dl = subprocess.run(cmd, stdout=subprocess.DEVNULL)

    if yt_dl.returncode:
        logger.error(f"There was an error {yt_dl.returncode} processing {url}")
        return []

    ids = []
    with open(downloaded_file, "r") as f:
        ids = f.read().splitlines()
    os.remove(downloaded_file)
    if ids == []:
        logger.info(f"No playlists found for playlist: {url}")
        return []
    else:
        logger.debug(f"List of {len(ids)} IDS captured from url {url}")
        return ids


def get_video_info(
    youtube_id,
    output_folder,
    progress_hook=None,
    thumbnail=True,
    subtitle=True,
    info=True,
):
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    logger.error("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢")
    folder = Path(output_folder)
    if not folder.exists():
        folder.mkdir(parents=True)
    else:
        logger.error(f"Cleaning out {folder}")
        for file in folder.glob("*"):
            logger.debug(f"Removing {file}")
            file.unlink()
    if progress_hook:
        hook = progress_hook
    else:
        hook = internal_hook

    ydl_opts = {
        # "logger": logger,
        "progress_hooks": [hook],
        "writethumbnail": thumbnail,
        "skip_download": True,
        "writeinfojson": info,
        "writeautomaticsub": subtitle,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
        "outtmpl": str(folder / "%(upload_date)s___%(id)s.%(ext)s"),
    }

    info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url)

        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        info = ydl.sanitize_info(info)
        files = [f for f in Path(output_folder).glob(f"*{youtube_id}*")]
        return info, files


def get_channel_info(id, output_folder, thumbnail=True, subtitle=True, info=True):
    # this command seemed to work. resulting file can be imported from downloads
    # tab
    # yt-dlp --write-info -o harry.txt https://www.youtube.com/@HarryMack
    pass


def get_playlist_info(id, output_folder, thumbnail=True, subtitle=True, info=True):
    # this function kinda works, but it keeps downloading
    # the videos. i manually downloaded the playlists 1 by 1
    # and put them in the for_input folder
    logger.error("🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵")
    url = f"https://www.youtube.com/playlist?list={id}"
    # url = f"https://www.youtube.com/@HarryMack/playlists"
    folder = Path(output_folder)
    if not folder.exists():
        folder.mkdir(parents=True)
    else:
        pass
        # use to clean out temp folder once
        # things are working
        # for file in folder.glob("*"):
        #     logger.debug(f"Removing {file}")
        #     file.unlink()

    # using 3 _ to split the date from the id since the id
    # can have underscores in it

    ydl_opts = {
        #  "logger": logger,
        "progress_hooks": [internal_hook],
        "writethumbnail": thumbnail,
        "skip_download": True,
        "writeinfojson": info,
        "clean_infojson": True,
        "playlist_items": None,
        "verbose": True,
        "outtmpl": str(folder / "%(upload_date)s___%(id)s"),
    }

    info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url)

        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return ydl.sanitize_info(info)


def download_video_file(
    id,
    output_folder,
    progress_hook=None,
):
    url = f"https://www.youtube.com/watch?v={id}"
    logger.error("🟣🟣🟣🟣🟣🟣🟣")
    folder = Path(output_folder)
    if not is_disk_full(folder):
        if not folder.exists():
            folder.mkdir(parents=True)
    else:
        logger.error(f"Disk is full: {folder}")
        raise Exception(f"Disk is full: {folder}")

    if progress_hook:
        hook = progress_hook
    else:
        hook = internal_hook

    ydl_opts = {
        # "logger": logger,
        "progress_hooks": [hook],
        "format": "bestvideo[height<=720]+bestaudio",
        "extract_audio": True,
        "outtmpl": str(folder / "%(upload_date)s___%(id)s.%(ext)s"),
    }

    info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url)
            files = [f for f in Path(output_folder).glob(f"*{id}*")]
            logger.debug(f"Files: {files}")

        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return ydl.sanitize_info(info), files


def download_video_info_from_id(
    id, download_path, thumbnail=True, subtitle=True, info=True
):
    logger.error("🔴🔴🔴🔴🔴🔴🔴🔴")
    video = get_video_info(id, download_path, thumbnail, subtitle, info)
    files = []
    for f in Path(download_path).glob(f"*{id}*"):
        files.append(f)
    if "error" in video.keys():
        return {
            "youtube_id": id,
            "title": "",
            "episode": "",
            "upload_date": "",
            "private": False,
            "error": True,
            "error_info": video["error_info"],
        }, ["errrrrrorrrr"]

    else:
        return {
            "youtube_id": video["id"],
            "title": video["title"],
            "upload_date": video["upload_date"],
            "duration": video["duration"],
            "description": video["description"],
            "url": video["webpage_url"],
            "private": False,
            "error": False,
            "error_info": "",
        }, files


def download_playlist_info(
    playlist_id, download_path, thumbnail=True, subtitle=True, info=True
):
    playlist = get_playlist_info(playlist_id, download_path, thumbnail, subtitle, info)
    files = []
    for f in Path(download_path).glob(f"*{id}*"):
        files.append(f)
    if "error" in playlist.keys():
        return {
            "youtube_id": id,
            "title": "",
            "episode": "",
            "upload_date": "",
            "private": False,
            "error": True,
            "error_info": playlist["error_info"],
        }, ["errrrrrorrrr"]

    else:
        return {
            "youtube_id": playlist["id"],
            "title": playlist["title"],
            "upload_date": playlist["upload_date"],
            "duration": playlist["duration"],
            "description": playlist["description"],
            "private": False,
            "error": False,
            "error_info": "",
        }, files
