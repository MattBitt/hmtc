from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel

# from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.section import Section
from hmtc.schemas.video import VideoItem
from hmtc.utils.ffmpeg_utils import rip_track
from hmtc.utils.lyric_utils import create_lyrics_file
from hmtc.utils.mutagen_utils import write_id3_tags

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


@dataclass
class TrackItem:
    # this (probably...) shouldn't be happening here.
    track_folder = WORKING / "tracks"
    if not track_folder.exists():
        track_folder.mkdir()
    id: int = None
    title: str = None
    track_number: int = 0
    length: int = 0
    album_id: int = None
    album_title: str = None

    def from_model(track: TrackModel) -> "TrackItem":
        return TrackItem(
            id=track.id,
            title=track.title,
            track_number=track.track_number,
            length=track.length,
            album_id=track.album_id,
        )

    def write_file(self, input_file: Path):

        album = AlbumModel.get_or_none(AlbumModel.id == self.album_id)
        section = SectionModel.get_or_none(SectionModel.track_id == self.id)
        num_tracks = (
            TrackModel.select(fn.Count(TrackModel.id))
            .where(TrackModel.album_id == album.id)
            .scalar()
        )
        if album is None or section is None:
            logger.error(f"album: {album}")
            logger.error(f"times: {section}")
            return
        out_folder = self.track_folder / f"{album.title}/"
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
            "album": album.title,
            "albumartist": "Harry Mack",
            "artist": "Harry Mack",
            "date": str(section.video.upload_date.year),
        }
        logger.debug(f"Writing tags {tags} to {output_file}")
        write_id3_tags(output_file, tags)
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
