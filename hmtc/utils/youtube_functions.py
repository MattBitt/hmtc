import yt_dlp
import subprocess
import os
from loguru import logger
from pathlib import Path


# this is here only to run this file from the command line

# from hmtc.utils.general import is_disk_full


def is_disk_full(folder):
    return False


######


# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading, now post-processing ...")


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
        logger.success("Playlist list captured")
        return ids


def get_video_info(id, output_folder, thumbnail=True, subtitle=True, info=True):
    url = f"https://www.youtube.com/watch?v={id}"
    folder = Path(output_folder)
    if not folder.exists():
        folder.mkdir(parents=True)
    else:
        pass
    ydl_opts = {
        "logger": logger,
        "progress_hooks": [my_hook],
        "writethumbnail": thumbnail,
        "skip_download": True,
        "writeinfojson": info,
        "writeautomaticsub": subtitle,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
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


def get_playlist_info(id, output_folder, thumbnail=True, subtitle=True, info=True):
    # this function kinda works, but it keeps downloading
    # the videos. i manually downloaded the playlists 1 by 1
    # and put them in the for_input folder

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
        # "logger": logger,
        # "progress_hooks": [my_hook],
        "writethumbnail": thumbnail,
        "skip_download": True,
        "writeinfojson": info,
        "clean_infojson": True,
        "playlist_items": None,
        "verbose": True,
        "outtmpl": str(folder / "%(id)s"),
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


def download_video_info_from_id(
    id, download_path, thumbnail=True, subtitle=True, info=True
):
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


if __name__ == "__main__":
    # harry mack's channel
    channel_url = "https://www.youtube.com/@HarryMack"

    # harry mack's playlists
    channel_playlists_url = channel_url + "/playlists"

    playlist_id = "PLtbrIhAJmrPBf2DKh3UByQ6Q1D_rCSAiI"
    # Harry Mack Channel Playlists
    playlists = [
        # "PLtbrIhAJmrPBf2DKh3UByQ6Q1D_rCSAiI",
        # "PLtbrIhAJmrPAoGPFsaQn5HCWoO5u4m1La",
        # "PLtbrIhAJmrPAVe4uNYJZvgkSFk9jKpW1t",
        # "PLtbrIhAJmrPCXcXB3GQFG-kpVcsnucw1k",
        # "PLtbrIhAJmrPAcktPEn7PgQO0yn8bmKeTJ",
        # "PLtbrIhAJmrPDVjUBHYPBOJYYC8sPhEILZ",
        # "PLtbrIhAJmrPAgM7MkLiO5CNeaaOZTZ86R",
        # "PLtbrIhAJmrPAGLnngi0ZOTvNmuNt5uHJk",
        # "PLtbrIhAJmrPD7NJ92Jr8s8JFGdmOmMS95",
        # "PLtbrIhAJmrPB0d7RFcZZlQEHQDAYUxBuz",
        #
        # "PLtbrIhAJmrPBXWuzE5TWOEmxbAYjg4o6G",
        # "PLtbrIhAJmrPALgw6Ko7H78WxHC3pzxeZl",
        # "PLtbrIhAJmrPAHZP4a8mtTaoA8Q4D9B8nb",
        # "PLtbrIhAJmrPCL-FRXUleIyt5KpS8X4MCW",
        # "PLtbrIhAJmrPBh0ZL7TPhFS58teh09JrGU",
        # "PLtbrIhAJmrPAzDyP5sErLt04JuOG4Jata",
        # "PLtbrIhAJmrPAVZCuoMVAFys0mkVvvNawA",
    ]
    # Harry Mack Clips Channel Playlists,
    playlists2 = [
        # "PLVuktCy_G9zJpHpXYVGCLggfwkjOx-y7g",
        # "PLVuktCy_G9zJXnTiZ3glQZCxWv1LgLyb3",
        # "PLVuktCy_G9zKTuvHZ7nt5nVpp9Uu6Hr6b",
        # "PLVuktCy_G9zJm10Pb88HWLFgGhTDGW0BE",
        # "PLVuktCy_G9zJqDdVAuYWwjjvvFfe4xSip",
        # "PLVuktCy_G9zLXQfWviOhqiOdvTp5MYbZZ",
        # "PLVuktCy_G9zKL9Ty5HiX33-C8aAoYj6mB",
        # "PLVuktCy_G9zJQcrnv5G9L1n3v4xOuRhj7",
        # "PLVuktCy_G9zJyN425vIieKSkWWy6U9qVB",
        # "PLVuktCy_G9zKaw65CQ-hmvM-8u0J3QCBM",
        # "PLVuktCy_G9zLqq_g0D44cKCE0xEmenRUQ",
        # "PLVuktCy_G9zJnQxmSVV_Hh-pqXZS3hVwU",
        # "PLVuktCy_G9zJ-jTzCIDEawC7FuvD5X46x",
        # "PLVuktCy_G9zL7CkgfIfr52ZOy8CXRnwVT",
        # "PLVuktCy_G9zLQwCsQi8mTxqzw6cl47aRH",
        # "PLVuktCy_G9zKRXGaCmeBHoq-Td40GQU67",
        "PLVuktCy_G9zIcBwxMKSBgtByiP6qhC84J",
    ]
    # i ain't gotta worry
    id = "3oPCYzT1ek4"
    # result = fetch_ids_from(url)
    for p in playlists2:
        get_playlist_info(
            p, "/mnt/c/DATA/repos/REPODATA/hmtc/downloads", True, True, True
        )
    # playlist = download_playlist_info(
    #     playlist_id=playlist_id,
    #     download_path="/mnt/c/DATA/repos/REPODATA/hmtc/downloads/",
    # )
    # if playlist:
    #     print(playlist)
