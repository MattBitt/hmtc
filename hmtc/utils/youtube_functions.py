import json
import os
import subprocess
from pathlib import Path

import yt_dlp
from loguru import logger

from hmtc.config import init_config

config = init_config()
WORKING = Path(config["WORKING"]) / "downloads"


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
        # print(msg)
        pass


# as of 1/14/25 this is correct. not sure if the
# last message was an error or something else
# changed.
# if url is channel it will grab all of the videos
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
        # logger.info(f"No playlists found for playlist: {url}")
        return []
    else:
        # logger.debug(f"List of {len(ids)} IDS captured from url {url}")
        return ids


def get_video_info(
    youtube_id,
    output_folder=WORKING,
    progress_hook=None,
):
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    logger.error("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢")
    folder = Path(output_folder)
    if not folder.exists():
        folder.mkdir(parents=True)
    else:
        # logger.error(f"Cleaning out {folder}")
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
        "writethumbnail": True,
        "skip_download": True,
        "writeinfojson": True,
        "writeautomaticsub": True,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
        # "cookiefile": ("\\\\wsl.localhost\\Ubuntu-22.04\\home\\matt\\programming\\hmtc\\hmtc\\utils\\cookies.txt"),
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
    output_folder=WORKING,
    progress_hook=None,
):
    url = f"https://www.youtube.com/watch?v={id}"
    folder = Path(output_folder)
    if not is_disk_full(folder):
        if not folder.exists():
            folder.mkdir(parents=True)
    else:
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
            return files
        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return []


def parse_youtube_info_file(file: Path):
    with open(file, "r") as f:
        all_data = f.read()
    data = json.loads(all_data)
    channel = {
        "title": data["channel"],
        "url": data["channel_url"],
        "youtube_id": data["channel_id"],
    }
    video = {
        "title": data["title"],
        "url": data["webpage_url"],
        "youtube_id": data["id"],
        "description": data["description"],
        "duration": data["duration"],
        "upload_date": data["upload_date"],
        "channel": channel,
    }
    return video


def download_channel_files(channel_id, url) -> Path:
    output_filename = WORKING / "%(channel_id)s.%(ext)s"
    ret = subprocess.call(
        [
            "yt-dlp",
            "--playlist-items",
            "0",
            "--write-info-json",
            "--write-thumbnail",
            url,
            "-o",
            output_filename,
        ]
    )
    if ret:
        raise Exception(f"Error downloading channel files for {channel_id}")
    else:
        logger.debug(f"Channel files downloaded for {channel_id}")
        new_files = [Path(f) for f in WORKING.glob(f"*{channel_id}*")]
        return new_files


if __name__ == "__main__":
    # data = parse_youtube_info_file(Path("hmtc/utils/yt.info.json"))
    # logger.debug(data)
    # files = download_channel_files(
    #    "UC59ZRYCHev_IqjUhremZ8Tg", "https://www.youtube.com/@HarryMack"
    # )
    # print(files)

    print(fetch_ids_from("https://www.youtube.com/channel/UC59ZRYCHev_IqjUhremZ8Tg"))
