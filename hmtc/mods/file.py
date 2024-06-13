from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
import shutil
from hmtc.utils.general import move_file, is_absolute
from hmtc.config import init_config
from hmtc.models import Video, get_file_type, File as FileModel
from peewee import fn

config = init_config()
WORKING = config["paths"]["working"]
STORAGE = config["paths"]["storage"]


@dataclass
class File:
    path: str
    filename: str  # this includes the extension
    folder: str = STORAGE

    @classmethod
    def from_path(cls, path: str) -> "File":
        if not File.folder:
            File.folder = STORAGE

        p = Path(File.folder) / path
        return cls(path=str(p.parent), filename=p.name)

    def move_to(self, dest: str) -> "File":

        destination = Path(File.folder) / dest
        if not destination.exists():
            logger.info(f"Creating folder {destination}")
            destination.mkdir(parents=True)
        old_file = Path(self.path) / self.filename
        new_file = destination / self.filename
        move_file(str(old_file), str(new_file))
        return File(path=str(new_file.parent), filename=new_file.name)

    def __str__(self) -> str:
        return f"{self.path}/{self.filename}"

    def __post_init__(self) -> None:
        try:
            # logger.debug(f"End of Section {self} __post_init__")
            p = Path(self.path)
            if not p.exists():
                raise ValueError(f"Folder does not exist: {self.path}")
            if not p.is_dir():
                raise ValueError(f"Path is not a folder: {self.path}")
            if not (p / self.filename).exists():
                raise ValueError(f"File does not exist: {self.path}/{self.filename}")

        except ValueError as e:
            logger.error(e)
            raise


@dataclass
class FileManager:

    @staticmethod
    def add_file_to_video(file: File, video: Video):
        filetype = get_file_type(file.filename)
        try:
            if not video:
                raise ValueError("Video object is required")
            if not file:
                raise ValueError("File object is required")

            logger.info(f"Adding {filetype} file ({file}) to {video}")
            # video.files.append(file)
            # video.save()
            logger.info(f"File added to {video}")

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def add_path_to_video(path: Path, video: Video):
        output_path = Path(STORAGE) / f"videos/{video.youtube_id}/"
        try:
            if not video:
                raise ValueError("Video object is required")
            if not path:
                raise ValueError("path object is required")
            file = File.from_path(path)
            filetype = get_file_type(file.filename)
            file.move_to(output_path)
            f = FileModel.create(
                path=str(output_path),
                filename=file.filename,
                file_type=filetype,
                video_id=video.id,
            )

            logger.info(f"Adding {file} to {video}")
            # video.files.append(file)
            # video.save()
            logger.info(f"File added to {video}")

        except Exception as e:
            logger.error(e)
            raise

    @staticmethod
    def get_duration_downloaded_videos(series=None):

        if series:
            duration = Video.select(fn.Sum(Video.duration)).where(
                (Video.series == series) & (Video.downloaded == True)
            )
            return duration.scalar()
