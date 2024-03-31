import yt_dlp
import subprocess
import os
from loguru import logger
from pathlib import Path


def fetch_video_ids_from(url):
    """
    playlist: dict with keys: name, url

    """

    # couldn't figure out how to get this list without saving it to disk first ...
    download_file = Path("downloads/ids.txt")
    cmd = (
        f"yt-dlp --flat-playlist --print-to-file id {str(download_file)} {url}".split()
    )
    yt_dl = subprocess.run(cmd, stdout=subprocess.DEVNULL)

    if yt_dl.returncode:
        logger.error(f"There was an error {yt_dl.returncode} processing {url}")
        return []

    ids = []
    with open(download_file, "r") as f:
        ids = f.read().splitlines()
    os.remove(download_file)
    if ids == []:
        logger.info(f"No videos found for playlist: {url}")
        return []
    else:
        logger.success("Video list captured")
        return ids


def get_video_info(id):
    url = f"https://www.youtube.com/watch?v={id}"
    # yt-dlp -o --verbose --skip_download --writeinfojson "https://www.youtube.com/watch?v=ijVGIcVRIbk"
    ydl_opts = {}
    info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return ydl.sanitize_info(info)


def download_video_info(id):
    video = get_video_info(id)
    if "error" in video.keys():
        return {
            "youtube_id": id,
            "title": "",
            "episode": "",
            "upload_date": "",
            "private": False,
            "error": True,
            "error_info": video["error_info"],
        }

    else:
        return {
            "youtube_id": video["id"],
            "title": video["title"],
            "upload_date": video["upload_date"],
            "duration": video["duration"],
            "description": video["description"],
            "private": False,
            "error": False,
            "error_info": "",
        }
