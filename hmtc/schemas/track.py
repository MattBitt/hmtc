from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import File as FileModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.base import BaseItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.ffmpeg_utils import rip_track
from hmtc.utils.jellyfin_functions import refresh_library
from hmtc.utils.lyric_utils import create_lyrics_file
from hmtc.utils.mutagen_utils import embed_image, write_id3_tags

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


@dataclass(frozen=True, kw_only=True)
class Track(BaseItem):
    # this (probably...) shouldn't be happening here.
    track_folder = WORKING / "tracks"
    if not track_folder.exists():
        track_folder.mkdir()
    id: int = None
    item_type: str = "TRACK"
    title: str = None
    track_number: int = 0
    length: int = 0
    album_id: int = 0
    album_title: str = None
    section: SectionItem = None
    files: list = field(default_factory=list)

    @staticmethod
    def from_model(track: TrackModel) -> "Track":
        if track.section is None:
            logger.debug(f"Track {track} has no section")
            section = None
        else:
            section = SectionItem.from_model(track.section.get())

        return Track(
            id=track.id,
            title=track.title,
            track_number=track.track_number,
            length=track.length,
            album_id=track.album.id,
            album_title=track.album.title,
            files=[FileItem.from_model(f) for f in track.files],
            section=SectionItem.from_model(track.section.get()),
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "track_number": self.track_number,
            "length": self.length,
            "album_id": self.album_id,
            "album_title": self.album_title,
            "files": [f.serialize() for f in self.files],
            "section": self.section.serialize(),
        }

    @staticmethod
    def update_from_dict(item_id, new_data):
        track = TrackModel.get_by_id(item_id)
        track.title = new_data["title"]
        track.track_number = new_data["track_number"]
        track.length = new_data["length"]
        track.album_id = new_data["album_id"]
        track.save()

    @staticmethod
    def delete_id(item_id):
        track = TrackModel.get_by_id(item_id)
        for file in track.files:
            FileManager.delete_file(file)
        track.delete_instance()

    def create_all_files(self, video: VideoItem):
        self.create_audio_file(video)
        self.create_lyrics_file(video)

    def create_audio_file(self, video: VideoItem):

        try:
            input_file = (
                FileModel.select()
                .where(
                    (FileModel.video_id == video.id) & (FileModel.file_type == "audio")
                )
                .get()
            )
        except:
            logger.error(f"No input audo file found for {video.title}")
            return

        input_file_path = Path(input_file.path) / input_file.filename
        image_file_path = FileManager.get_file_for_video(video, "poster")
        im_file = Path(image_file_path.path) / image_file_path.filename
        track_path = self.write_audio_file(
            input_file=input_file_path, image_file=im_file
        )
        new_audio_file = FileManager.add_path_to_track(
            path=track_path, track=self, video=video
        )
        logger.debug(f"Created audio file {new_audio_file}")

    def create_lyrics_file(self, video: VideoItem):
        try:
            input_file = (
                FileModel.select()
                .where(
                    (FileModel.video_id == video.id)
                    & (FileModel.file_type == "subtitle")
                )
                .get()
            )
        except:
            logger.error(f"No input file found for")
            return
        input_file_path = Path(input_file.path) / input_file.filename
        lyrics_path = self.write_lyrics_file(input_file_path)
        new_lyrics_file = FileManager.add_path_to_track(
            path=lyrics_path, track=self, video=video
        )
        logger.debug(f"Created lyrics file {new_lyrics_file}")

    def write_audio_file(self, input_file: Path, image_file: Path):
        album_title = AlbumModel.get_or_none(AlbumModel.id == self.album_id).title
        section = (
            SectionModel.select().where(SectionModel.track_id == self.id).get_or_none()
        )
        if section is None or album_title is None:
            logger.error(f"section: {section}")
            logger.error(f"album_title: {album_title}")
            return

        out_folder = self.track_folder / f"{album_title}/"
        if not out_folder.exists():
            out_folder.mkdir(parents=True)
        output_file = out_folder / f"{self.track_number} - {self.title}.mp3"
        if output_file.exists():
            logger.error(f"File {output_file} already exists. Deleting")
            output_file.unlink()

        logger.error(
            f"Ripping track from {input_file} to {str(output_file)} from {section.start} to {section.end}"
        )
        rip_track(
            input_file,
            str(output_file),
            start_time=section.start / 1000,
            end_time=section.end / 1000,
        )
        # need to actually add the output file to the DB and move it
        # to the storage location
        # how did i do it in the tests?
        tags = {
            "title": self.title,
            "tracknumber": f"{self.track_number}",
            "album": album_title,
            "albumartist": "Harry Mack",
            "artist": "Harry Mack",
            "date": str(section.video.upload_date.year),
        }
        logger.debug(f"Writing tags {tags} to {output_file}")
        write_id3_tags(output_file, tags)
        embed_image(audio_file=output_file, image_file=image_file)
        refresh_library()
        return output_file

    def write_lyrics_file(self, input_file: Path):
        album = AlbumModel.get_or_none(AlbumModel.id == self.album_id)
        section = SectionModel.get_or_none(SectionModel.track_id == self.id)
        if album is None or section is None:
            logger.error(f"album: {album}")
            logger.error(f"times: {section}")
            return
        out_folder = self.track_folder / f"{album.title}/"
        if not out_folder.exists():
            out_folder.mkdir(parents=True)
        # this needs to match the mp3 name for jellyfin to pick it up
        output_file = out_folder / f"{self.track_number} - {self.title}.lrc"
        if output_file.exists():
            logger.error(f"File {output_file} already exists. Deleting")
            output_file.unlink()

        logger.error(
            f"Creating lyrics file from {input_file} to {str(output_file)} from {section.start} to {section.end}"
        )
        create_lyrics_file(
            input_file=input_file, output_file=output_file, section=section
        )
        return output_file

    # 🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝🥝
    # 10/18/24 - the code below may or not be useful. I think i created it
    # to get some tracks built before our vacation to chicago. leaving it
    # in for now., but don't add anything here

    # @staticmethod
    # def old_create_from_section(video: VideoItem, album, section: Section) -> "TrackItem":
    #     logger.error(f"Creating track from section {section} for video {video}")
    #     title = video.title
    #     if title is None:
    #         logger.error(f"Video {video} has no title. Skipping")
    #         return None
    #     video_id = video.id
    #     track_number = AlbumItem.get_next_track_number(album)
    #     epno = None
    #     if album is not None:
    #         album_id = album.id
    #         if TrackItem.album_title is None:
    #             is_omegle, epno = is_omegle_bars(video.title)
    #             if is_omegle:
    #                 TrackItem.album_title = f"Omegle Bars {epno}"
    #             else:
    #                 TrackItem.album_title = album.title
    #     start_time = section.start
    #     end_time = section.end
    #     if epno is None:
    #         epno = 0
    #     t = TrackItem(
    #         title=f"{epno}.{track_number}",
    #         track_number=track_number,
    #         video_id=video_id,
    #         album_id=album_id,
    #         start_time=start_time,
    #         end_time=end_time,
    #     )
    #     t.save_to_db()
    #     return t

    def save_to_db(self):
        logger.error(f"Saving track {self}")
        track = TrackModel(
            title=self.title,
            track_number=self.track_number,
            length=self.length,
            album_id=self.album_id,
        )
        track.save()
