from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.dtos.track import TrackDTO
from hmtc.models import File as FileModel
from hmtc.models import Video, get_file_type
from hmtc.utils.ffmpeg_utils import extract_audio
from hmtc.utils.general import move_file

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
            if filetype == "video":
                audio = FileManager.extract_audio(file)
                audio_file = File.from_path(audio)
                audio_file.move_to(output_path)
                f = FileModel.create(
                    path=str(output_path),
                    filename=audio_file.filename,
                    file_type="audio",
                    video_id=video.id,
                )

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

    @staticmethod
    def extract_audio(file: File):
        try:
            if not file:
                raise ValueError("File object is required")
            logger.info(f"Extracting audio from {file}")
            vid_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm"]
            for ve in vid_extensions:
                if ve in file.filename:
                    outfile = Path(file.path) / (file.filename.replace(ve, ".mp3"))
                    break
            logger.debug(f"Extracting audio from {file} to {outfile}")
            extract_audio(input=str(file), output=str(outfile))
            return outfile

        except Exception as e:
            logger.error(e)
            raise

    @staticmethod
    def get_file_for_video(video: Video, filetype: str):
        try:
            if not video:
                raise ValueError("Video object is required")
            if not filetype:
                raise ValueError("Filetype is required")

            file = FileModel.get_or_none(
                (FileModel.video_id == video.id) & (FileModel.file_type == filetype)
            )
            if not file:
                logger.debug(f"No {filetype} file found for {video}")
                return

            return File(path=file.path, filename=file.filename)

        except Exception as e:
            logger.error(e)
            raise

    @staticmethod
    def add_file_to_track(file: File, track: TrackDTO):
        pass
        # filetype = get_file_type(file.filename)
        # try:
        #     if not video:
        #         raise ValueError("Video object is required")
        #     if not file:
        #         raise ValueError("File object is required")

        #     logger.info(f"Adding {filetype} file ({file}) to {video}")
        #     # video.files.append(file)
        #     # video.save()
        #     logger.info(f"File added to {video}")

        # except ValueError as e:
        #     logger.error(e)
        #     raise

    @staticmethod
    def add_path_to_track(path: Path, track: TrackDTO):
        pass
        # output_path = Path(STORAGE) / f"tracks/{track.youtube_id}/"
        # try:
        #     if not track:
        #         raise ValueError("Track object is required")
        #     if not path:
        #         raise ValueError("path object is required")
        #     file = File.from_path(path)
        #     filetype = get_file_type(file.filename)
        #     if filetype == "track":
        #         audio = FileManager.extract_audio(file)
        #         audio_file = File.from_path(audio)
        #         audio_file.move_to(output_path)
        #         f = FileModel.create(
        #             path=str(output_path),
        #             filename=audio_file.filename,
        #             file_type="audio",
        #             track_id=track.id,
        #         )

        #     file.move_to(output_path)
        #     f = FileModel.create(
        #         path=str(output_path),
        #         filename=file.filename,
        #         file_type=filetype,
        #         track_id=track.id,
        #     )

        #     logger.info(f"Adding {file} to {track}")
        #     # track.files.append(file)
        #     # track.save()
        #     logger.info(f"File added to {track}")

        # except Exception as e:
        #     logger.error(e)
        #     raise
