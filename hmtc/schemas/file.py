import os
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.models import get_file_type
from hmtc.utils.ffmpeg_utils import extract_audio
from hmtc.utils.general import move_file, my_copy_file

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

    def copy_to(self, dest: str) -> "File":
        destination = Path(File.folder) / dest
        if not destination.exists():
            logger.info(f"Creating folder {destination}")
            destination.mkdir(parents=True)
        old_file = Path(self.path) / self.filename
        new_file = destination / self.filename
        my_copy_file(str(old_file), str(new_file))
        return File(path=str(new_file.parent), filename=new_file.name)

    def make_a_temporary_copy(self) -> "File":
        temp_folder = Path(WORKING) / "temp"
        if not temp_folder.exists():
            temp_folder.mkdir(parents=True)
        temp_file = temp_folder / self.filename
        my_copy_file(str(Path(self.path) / self.filename), str(temp_file))
        return File(path=str(temp_file.parent), filename=temp_file.name)

    def move_to(self, dest: str) -> "File":
        destination = Path(File.folder) / dest
        if not destination.exists():
            logger.info(f"Creating folder {destination}")
            destination.mkdir(parents=True)
        old_file = Path(self.path) / self.filename
        new_file = destination / self.filename
        move_file(str(old_file), str(new_file))
        return File(path=str(new_file.parent), filename=new_file.name)

    def rename(self, new_name: str) -> "File":
        old_file = Path(self.path) / self.filename
        new_file = Path(self.path) / new_name
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
    def add_file_to_video(file: File, video: VideoModel):
        filetype = get_file_type(file.filename)
        try:
            if not video:
                raise ValueError("Video object is required")
            if not file:
                raise ValueError("File object is required")

            # logger.info(f"Adding {filetype} file ({file}) to {video}")
            # video.files.append(file)
            # video.save()
            logger.info(f"File added to {video.title}")

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def add_path_to_video(path: Path, video: VideoModel):
        output_path = Path(STORAGE) / f"videos/{video.youtube_id}/"
        try:
            if not video:
                raise ValueError("Video object is required")
            if not path:
                raise ValueError("path object is required")

            file = File.from_path(path)
            filetype = get_file_type(file.filename)

            if filetype == "album_nfo":
                existing_files = FileModel.select().where(
                    (FileModel.video_id == video.id)
                    & (FileModel.file_type == "album_nfo")
                )
                for ef in existing_files:

                    logger.info(f"File {file} already exists for {video}")
                    logger.debug("Deleting existing album_nfo")
                    ef.delete_instance()

            if filetype == "video":
                audio = FileManager.extract_audio(file)
                audio_file = File.from_path(audio)
                audio_file.move_to(output_path)
                FileModel.create(
                    path=str(output_path),
                    filename=audio_file.filename,
                    file_type="audio",
                    video_id=video.id,
                )

            file.move_to(output_path)
            FileModel.create(
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
            duration = VideoModel.select(fn.Sum(VideoModel.duration)).where(
                (VideoModel.series == series) & (VideoModel.downloaded == True)
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
    def get_file_for_video(video: VideoModel, filetype: str):
        try:
            if not video:
                raise ValueError("Video object is required")
            if not filetype:
                raise ValueError("Filetype is required")

            file = FileModel.get_or_none(
                (FileModel.video_id == video.id) & (FileModel.file_type == filetype)
            )
            if not file:
                # logger.debug(f"No {filetype} file found for {video.title}")
                return File(path="hmtc/assets/images", filename="no-image.png")

            return File(path=file.path, filename=file.filename)

        except Exception as e:
            logger.error(e)
            raise

    @staticmethod
    def get_file_for_album(album: AlbumModel, filetype: str):
        try:
            if not album:
                raise ValueError("AlbumModel object is required")
            if not filetype:
                raise ValueError("Filetype is required")

            file = FileModel.get_or_none(
                (FileModel.album_id == album.id) & (FileModel.file_type == filetype)
            )
            if not file:
                # 🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣
                # need to adjust this for aspect ratio and size of the image
                return File(path="hmtc/assets/images", filename="no-image.png")

            return File(path=file.path, filename=file.filename)

        except Exception as e:
            logger.error(e)
            raise

    ## 🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵
    ## copied the below from the same functions above and
    ## changed it to tracks instead of videos
    # 10/20/24
    @staticmethod
    def add_file_to_track(file: File, track: TrackModel):
        filetype = get_file_type(file.filename)
        try:
            if not track:
                raise ValueError("Track object is required")
            if not file:
                raise ValueError("File object is required")

            # logger.info(f"Adding {filetype} file ({file}) to {track}")
            # track.files.append(file)
            # track.save()
            logger.info(f"File added to {track.title}")

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def add_path_to_track(path: Path, track: TrackModel, video: VideoModel):
        try:
            album_title = video.album.title
        except Exception as e:
            logger.error(e)
            album_title = "Unknown Album"
        output_path = Path(STORAGE) / f"tracks/Harry Mack/{album_title}/"
        try:
            if not track:
                raise ValueError("Track object is required")
            if not path:
                raise ValueError("path object is required")

            file = File.from_path(path)
            filetype = get_file_type(file.filename)

            if filetype == "album_nfo":
                existing_files = FileModel.select().where(
                    (FileModel.track_id == track.id)
                    & (FileModel.file_type == "album_nfo")
                )
                for ef in existing_files:

                    logger.info(f"File {file} already exists for {track}")
                    logger.debug("Deleting existing album_nfo")
                    ef.delete_instance()

            if filetype == "video":
                audio = FileManager.extract_audio(file)
                audio_file = File.from_path(audio)
                audio_file.move_to(output_path)
                FileModel.create(
                    path=str(output_path),
                    filename=audio_file.filename,
                    file_type="audio",
                    track_id=track.id,
                )

            file.move_to(output_path)
            f = FileModel.create(
                path=str(output_path),
                filename=file.filename,
                file_type=filetype,
                track_id=track.id,
            )

            return f

        except Exception as e:
            logger.error(e)
            raise

    # 10/21/24 copied this method again from track and using it for album
    @staticmethod
    def add_path_to_album(path: Path, album: AlbumModel):
        try:
            album_title = album.title
        except Exception as e:
            logger.error(e)
            album_title = "Unknown Album"

        output_path = Path(STORAGE) / f"tracks/Harry Mack/{album_title}/"

        if not album:
            raise ValueError("Album object is required")
        if not path:
            raise ValueError("path object is required")

        try:
            file = File.from_path(path)
            filetype = get_file_type(file.filename)
            if filetype == "poster":
                # jellyfin uses cover.jpg for album art
                ext = Path(file.filename).suffix[1:]
                if ext not in ["jpg", "jpeg", "png"]:
                    raise ValueError(f"Invalid file type {ext} for album art")
                file.rename(f"cover.{ext}")
        except Exception as e:
            logger.error(e)
            raise
        try:

            file.move_to(output_path)
        except Exception as e:
            logger.error(f"Error moving file {file} to {output_path}")
            logger.error(e)
        f = FileModel.create(
            path=str(output_path),
            filename=file.filename,
            file_type=filetype,
            album_id=album.id,
        )

        return f

    @staticmethod
    def add_file_item_to_album(file: File, album: AlbumModel):
        if not album:
            raise ValueError("album object is required")
        if not file:
            raise ValueError("File object is required")
        output_path = Path(STORAGE) / f"tracks/Harry Mack/{album.title}/"
        filetype = get_file_type(file.filename)

        file.move_to(output_path)
        f = FileModel.create(
            path=str(output_path),
            filename=file.filename,
            file_type=filetype,
            album_id=album.id,
        )
        if filetype == "poster":
            # jellyfin uses cover.xxx for album art
            ext = Path(file.filename).suffix[1:]
            if ext not in ["jpg", "jpeg", "png", "webp"]:
                raise ValueError(f"Invalid file type {ext} for album art")
            os.rename(f"{output_path}/{file.filename}", f"{output_path}/cover.{ext}")
        f.filename = f"cover.{ext}"
        f.save()
        return f

    @staticmethod
    def delete_audio_file_from_track(track_id, file_type):
        track = TrackModel.get_by_id(track_id)
        audio_file = FileModel.get(
            (FileModel.track_id == track.id) & (FileModel.file_type == file_type)
        )
        audio_file_path = Path(audio_file.path) / audio_file.filename
        audio_file.delete_instance()
        os.remove(audio_file_path)
