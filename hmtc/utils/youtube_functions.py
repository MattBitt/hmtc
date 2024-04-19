import yt_dlp
import subprocess
import os
from loguru import logger
from pathlib import Path
from hmtc.utils.general import is_disk_full


# this seems to work for playlists and channels
def fetch_video_ids_from(url, download_path="."):
    """
    playlist: dict with keys: name, url

    """

    # couldn't figure out how to get this list without saving it to disk first ...
    download_file = Path(download_path) / "ids.txt"
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


def get_video_info(id, output_folder):
    url = f"https://www.youtube.com/watch?v={id}"
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
        "writethumbnail": True,
        "skip_download": True,
        "writeinfojson": True,
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


def download_media_files(id, output_folder):
    url = f"https://www.youtube.com/watch?v={id}"
    folder = Path(output_folder)
    if not is_disk_full(folder):
        if not folder.exists():
            folder.mkdir(parents=True)
    else:
        logger.error(f"Disk is full: {folder}")
        raise Exception(f"Disk is full: {folder}")
        # using 3 _ to split the date from the id since the id
    # can have underscores in it
    ydl_opts = {
        "writethumbnail": False,
        "skip_download": False,
        "writeinfojson": False,
        "formats": ["247", "251"],
        "outtmpl": str(folder / "%(upload_date)s___%(id)s"),
    }

    info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url)

            files = []
            for f in Path(output_folder).glob(f"*{id}*"):
                files.append(f)

        except Exception as e:
            logger.error(e)
            info["error"] = True
            info["error_info"] = e
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        return ydl.sanitize_info(info), files


def download_video_info(id, download_path):
    video = get_video_info(id, download_path)
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
            "private": False,
            "error": False,
            "error_info": "",
        }, files


if __name__ == "__main__":
    # harry mack's channel
    url = "https://www.youtube.com/channel/UC59ZRYCHev_IqjUhremZ8Tg"

    # i ain't gotta worry
    id = "3oPCYzT1ek4"
    result = download_media_files(id, ".")
    if result:
        print(result)
