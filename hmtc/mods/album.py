from dataclasses import dataclass
from typing import List

from loguru import logger

from hmtc.models import Album as AlbumTable, Track as TrackTable
from hmtc.mods.section import SectionManager, Section
from hmtc.schemas.video import VideoItem


@dataclass
class Track:
    title: str
    track_number: int
    duration: int
    album_id: int = None
    id: int = None


@dataclass
class Album:
    video_id: int
    title: str
    tracks: List[Track]

    def delete_album(self):
        logger.info(f"Deleting {self.title}")
        album_row = (
            AlbumTable.select().where(AlbumTable.video_id == self.video_id).first()
        )
        album_row.delete_instance()
        logger.info("Album deleted")

    @staticmethod
    def create_for_video(video: VideoItem):
        try:
            if not video:
                raise ValueError("Video object is required")

            logger.info(f"Creating album for {video}")
            # this shouldn't be a problem in production
            # famous last words...
            if video.title == "" or video.title is None:
                video.title = video.youtube_id

            try:
                AlbumTable.create(video_id=video.id, title=video.title)
                album = Album(video_id=video.id, title=video.title, tracks=[])
            except Exception as e:
                logger.error(e)
                raise

            logger.info("Album created")

            return album

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def grab_for_video(video_id: int):

        if not video_id:
            raise ValueError("Video object is required")

        try:
            album = AlbumTable.select().where(AlbumTable.video_id == video_id).first()
            logger.info(f"Album grabbed {album.title}")
        except Exception as e:
            logger.error(e)
            album = None
            logger.info(f"No album found for video {video_id}")
        if album:
            return Album(video_id=album.video_id, title=album.title, tracks=[])
        else:
            return None

    # @staticmethod
    # def create_tracks_for_video(video: VideoItem):
    #     if not video:
    #         raise ValueError("Video object is required")

    #     logger.info(f"Creating track for {video}")
    #     sections = None  # video load sections
    #     sm = SectionManager.from_video(video)
    #     sections = sm.sections
    #     if sections is not None:
    #         tracks = []
    #         for section in video.sections:
    #             track = Track(
    #                 title="Some random title",
    #                 track_number=len(tracks),
    #                 duration=section.duration,
    #                 album_id=video.album_id,
    #             )
    #             tracks.append(track)

    #         return tracks
    #     else:
    #         return None

    @staticmethod
    def update_album(title, video_id):
        if not video_id:
            raise ValueError("Video object is required")
        if title == "":
            raise ValueError("Title is required")

        album = AlbumTable.select().where(AlbumTable.video_id == video_id).first()
        album.title = title
        album.save()

    def add_track(self, section: Section):
        logger.debug(f"Adding track {section} to {self.title}")

    @staticmethod
    def get_next_track_number(album: "Album"):
        if not album:
            raise ValueError("Album object is required")
        t = TrackTable.select().where(TrackTable.album_id == album.id).count()
        return t + 1
