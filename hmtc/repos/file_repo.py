import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger

from hmtc.config import init_config
from hmtc.models import AudioFile, BaseModel, ImageFile, InfoFile, VideoFile

VIDEOS = [".mkv", ".mp4", ".webm"]
AUDIOS = [".mp3", ".wav"]
LYRICS = [".lrc"]
SUBTITLES = [".srt", ".en.vtt"]
INFOS = [".nfo", ".info.json", ".json", ".txt"]
POSTERS = [".jpg", ".jpeg", ".png", ".webp"]


class MyImage: ...


def MOVE_FILE(source: Path, target: Path):
    if not target.parent.exists():
        target.parent.mkdir(parents=True)
    try:
        # need to do this better....
        final_file = source.rename(target)
    except OSError as e:
        logger.debug(f"Error moving file {source} to storage: {e}")
        if e.errno == 18:  # Invalid cross-device link
            shutil.move(source, target)
            final_file = target
        else:
            raise Exception(f"Error moving file {source} to storage: {e}")
    if target != final_file:
        logger.error(f"Something fishy is happening")

    return final_file


def get_filetype(file: Path):
    file_string = str(file)

    if file_string.endswith(tuple(VIDEOS)):
        return "video"

    if file_string.endswith(tuple(AUDIOS)):
        return "audio"

    if file_string.endswith(tuple(INFOS)):
        return "info"

    if file_string.endswith(tuple(SUBTITLES)):
        return "subtitles"

    if file_string.endswith(tuple(LYRICS)):
        return "lyrics"

    if file_string.endswith(tuple(POSTERS)):
        return "poster"

    raise ValueError(f"Invalid filetype for {file_string}")


def process_file(file, target_path, final_name):
    _x = Path(target_path) / final_name

    file_dict = dict(
        file_size=round(file.stat().st_size / 1024),  # kbytes
        modified_datetime=datetime.fromtimestamp(file.stat().st_mtime),
        path=_x,
        hash=None,  # TBD
    )

    filetype = get_filetype(file)
    match filetype:

        case "audio":
            # going to use a better format
            # will rerip or redownload if needed in production
            if str(file).endswith(".mp3"):
                file.unlink()
                logger.error(f"Removed MP3 file {file}")
                new_file = None
            else:
                _path = Path(target_path) / final_name
                MOVE_FILE(file, _path)
                file_dict["bitrate"] = 345
                file_dict["sample_rate"] = 38
                file_dict["channels"] = 2
                file_dict["duration"] = 19831
                AudioFile.create(**file_dict)

        case "video":
            _path = Path(target_path) / final_name
            MOVE_FILE(file, _path)
            file_dict["duration"] = 100
            file_dict["frame_rate"] = 19.1
            file_dict["width"] = 1000
            file_dict["height"] = 1000
            file_dict["codec"] = "who knows"

            new_file = VideoFile.create(**file_dict)

        case "info":
            MOVE_FILE(file, _x)
            new_file = InfoFile.create(**file_dict)
        case "lyrics":
            raise NotImplemented("Lyrics - process file")
        case "subtitles":
            raise NotImplemented("Subittles - process file")
        case _:
            raise Exception(f"Filetype {filetype}")
    return {filetype: new_file}


def table_from_string(filetype) -> BaseModel:
    match filetype:
        case "audio":
            return AudioFile
        case "video":
            return VideoFile
        case "info":
            return InfoFile
        # probably need to rethink this
        # (poster vs image)
        # and this whole function...
        case "poster":
            return ImageFile
        case "lyrics":
            return "LyricFile"
        case "subtitle":
            return "SubtitleFile"


class FileRepo:

    def __init__(self, model: BaseModel):
        self.model = model

    def add(self, item: BaseModel, file: Path) -> None:
        filetype = get_filetype(file)
        if filetype in self.model.FILETYPES:
            target_path = self.model.PATH / item.youtube_id
            final_name = item.youtube_id + ".info.json"
            try:
                # move the file to its final destination
                new_file_dict = process_file(file, target_path, final_name)
            except Exception as e:
                logger.error(f"Error adding a file {file} to item {item.id}")
                raise e
            self.model.create(item_id=item.id, **new_file_dict)
        else:
            raise ValueError(f"Filetype not found while ADDING {file}")

    def get(self, item_id: int, filetype: str) -> Path:
        if filetype in self.model.FILETYPES:
            tbl = table_from_string(filetype)  # AudioFile table
            res1 = (
                self.model.select().where((self.model.item_id == item_id)).get_or_none()
            )
            if res1 is not None:
                res2 = tbl.get_or_none(res1.item_id)
            return res2
        else:
            raise ValueError(f"{filetype} file not found WHILE GETTING item {item_id}")

    def delete_files(self, item_id):
        item_file_row = (
            self.model.select().where((self.model.item_id == item_id)).get_or_none()
        )  # AlbumFiles

        for filetype in self.model.FILETYPES:

            if filetype == "info":
                info_file = Path(item_file_row.info.path)
                info_file.unlink()
                file_id = item_file_row.info.id
                item_file_row.info = None
                item_file_row.save()

                logger.debug(f"Found {filetype} file. Deleting")

                res2 = InfoFile.select().where(InfoFile.id == file_id).get()
                res2.delete_instance()
        item_file_row.delete_instance()

        # return res2.get_or_none()

    def poster(self) -> "MyImage":
        """Get poster image file"""
        return MyImage(self.get("poster"))

    def mp3(self) -> Path:
        """Get audio file path"""
        return Path(self.get("audio"))

    def mkv(self) -> Path:
        """Get video file path"""
        return Path(self.get("video"))
