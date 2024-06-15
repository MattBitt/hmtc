from dataclasses import dataclass
from pathlib import Path
from typing import List
from loguru import logger
from hmtc.schemas.video import VideoItem
from hmtc.models import Album as AlbumTable
from hmtc.mods.file import FileManager
from hmtc.mods.section import SectionManager


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

    @staticmethod
    def delete_album(album: "Album"):
        try:
            if not album:
                raise ValueError("Album object is required")

            # this should probably delete the tracks too
            logger.info(f"Deleting {album}")
            # album.delete_instance()
            logger.info(f"Album deleted")

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def create_for_video(video: VideoItem):
        try:
            if not video:
                raise ValueError("Video object is required")

            logger.info(f"Creating album for {video}")
            tracks = Album.create_tracks_for_video(video)
            try:
                AlbumTable.create(video_id=video.id, name=video.title, tracks=tracks)
            except Exception as e:
                logger.error(e)
                raise
            album = Album(video_id=video.id, name=video.title, tracks=tracks)
            logger.info(f"Album created")

            return album

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def grab_for_video(video_id: int):
        try:
            if not video_id:
                raise ValueError("Video object is required")
            album = VideoItem.get_album(video_id)
            logger.info(f"Grabbing album for {video_id}")
            if not album:
                logger.debug("No Album Found...")
                return None

            logger.info(f"Album grabbed {album.name}")
            return album

        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def create_tracks_for_video(video: VideoItem):

        if not video:
            raise ValueError("Video object is required")

        logger.info(f"Creating track for {video}")
        sections = None  # video load sections
        sm = SectionManager.from_video(video)
        sections = sm.sections
        if sections is not None:
            tracks = []
            for section in video.sections:
                track = Track(
                    title=section.title,
                    track_number=len(tracks),
                    duration=section.duration,
                    album_id=video.album_id,
                )
                tracks.append(track)

            return tracks
        else:
            return None
