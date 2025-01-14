import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import ffmpeg
from loguru import logger
from PIL import Image

from hmtc.config import init_config
from hmtc.models import (
    AudioFile,
    BaseModel,
    ImageFile,
    InfoFile,
    LyricFile,
    SubtitleFile,
    VideoFile,
)

VIDEOS = [".mkv", ".mp4", ".webm"]
AUDIOS = [".mp3", ".wav"]
LYRICS = [".lrc"]
# not sure if i need to support srt as well
SUBTITLES = [".en.vtt"]
INFOS = [".nfo", ".info.json", ".json", ".txt"]
POSTERS = [".jpg", ".jpeg", ".png", ".webp"]


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
        return "subtitle"

    if file_string.endswith(tuple(LYRICS)):
        return "lyrics"

    if file_string.endswith(tuple(POSTERS)):
        return "poster"

    raise ValueError(f"Invalid filetype for {file_string}")


def get_image_properties(image):
    with Image.open(image) as img:
        width, height = img.size
        colorspace = img.mode
    return width, height, colorspace


def get_audio_properties(audio):
    # Replace 'your_audio_file.mp3' with the path to your audio file
    probe = ffmpeg.probe(audio)

    # Access audio stream information
    audio_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None
    )

    if audio_stream:
        codec = audio_stream["codec_name"]
        bitrate = audio_stream["bit_rate"]
        channels = audio_stream["channels"]
        sample_rate = audio_stream["sample_rate"]
        duration = round(float(probe["format"]["duration"]))
        return codec, bitrate, channels, sample_rate, duration
    else:
        raise Exception(f"Error getting audio stream from {audio}")


def get_video_properties(filename):
    try:
        probe = ffmpeg.probe(filename)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        if video_stream is None:
            print("No video stream found.")
            return

        width = int(video_stream["width"])
        height = int(video_stream["height"])
        duration = round(float(probe["format"]["duration"]))
        codec = video_stream["codec_name"]
        if "nb_frames" in video_stream.keys():
            fps = float(video_stream["nb_frames"]) / float(video_stream["duration"])
        else:
            # not sure what determines if nb_frames is used or not...
            if "r_frame_rate" in video_stream.keys():
                r = video_stream["r_frame_rate"]
                if len(r) == 4:
                    fps = int(r[:2])
                else:
                    fps = -20
            else:
                fps = -1

        return width, height, duration, codec, fps

    except ffmpeg.Error as e:
        print(f"Error probing file: {e.stderr}")


def process_file(file, target, stem):

    file_dict = dict(
        file_size=round(file.stat().st_size / 1024),  # kbytes
        modified_datetime=datetime.fromtimestamp(file.stat().st_mtime),
        path=target / stem,
        hash=None,  # TBD
    )

    filetype = get_filetype(file)

    match filetype:

        case "poster":
            final_path = file_dict["path"].with_suffix(".webp")
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path

            height, width, colorspace = get_image_properties(final_path)
            file_dict["height"] = height
            file_dict["width"] = width
            file_dict["colorspace"] = colorspace

            new_file = ImageFile.create(**file_dict)

        case "audio":
            final_path = file_dict["path"].with_suffix(file.suffix)
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path
            codec, bitrate, channels, sample_rate, duration = get_audio_properties(
                final_path
            )
            file_dict["codec"] = codec
            file_dict["bitrate"] = bitrate
            file_dict["sample_rate"] = sample_rate
            file_dict["channels"] = channels
            file_dict["duration"] = duration
            new_file = AudioFile.create(**file_dict)

        case "video":
            final_path = file_dict["path"].with_suffix(file.suffix)
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path

            width, height, duration, codec, fps = get_video_properties(final_path)
            file_dict["duration"] = duration
            file_dict["fps"] = fps
            file_dict["width"] = width
            file_dict["height"] = height
            file_dict["codec"] = codec

            new_file = VideoFile.create(**file_dict)

        case "info":
            final_path = file_dict["path"].with_suffix(".info.json")
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path

            new_file = InfoFile.create(**file_dict)

        case "lyrics":
            final_path = file_dict["path"].with_suffix(".lrc")
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path

            new_file = LyricFile.create(**file_dict)

        case "subtitle":
            final_path = file_dict["path"].with_suffix(".en.vtt")
            if file.parent != target.parent:
                MOVE_FILE(file, final_path)
            file_dict["path"] = final_path
            new_file = SubtitleFile.create(**file_dict)
        case _:
            raise Exception(f"Filetype {filetype}")

    return {"filetype": filetype, "file": new_file}


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
            return LyricFile
        case "subtitle":
            return SubtitleFile


class FileRepo:

    def __init__(self, model: BaseModel):
        self.model = model

    def add(self, item: BaseModel, source: Path, target_path: Path, stem: str) -> None:
        filetype = get_filetype(source)
        if filetype in self.model.FILETYPES:
            try:
                # move the file to its final destination
                new_file_dict = process_file(source, target_path, stem)
            except Exception as e:
                logger.error(f"Error adding a file {source} to item {item.id}")
                raise e

            item, created = self.model.get_or_create(item_id=item.id)
            setattr(item, new_file_dict["filetype"], new_file_dict["file"])
            item.save()
            logger.success(f"Added {filetype} file to {item}")
        else:
            raise ValueError(f"Filetype not found while ADDING {source}")

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
        )

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

    def mp3(self) -> Path:
        """Get audio file path"""
        return Path(self.get("audio"))

    def mkv(self) -> Path:
        """Get video file path"""
        return Path(self.get("video"))

    def num_files(self, another_item_id):
        item = (
            self.model.select()
            .where(self.model.item_id == another_item_id)
            .get_or_none()
        )
        if item is None:
            return 0

        _counter = 0

        for filetype in self.model.FILETYPES:
            col = getattr(item, filetype)
            if col is not None:
                _counter += 1

        return _counter

    def my_files(self, item_id):
        item = self.model.select().where(self.model.item_id == item_id).get_or_none()
        if item is None:
            return []
        _files = []
        for filetype in self.model.FILETYPES:
            _files.append(self.get(item_id, filetype))
        return _files
