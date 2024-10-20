from dataclasses import dataclass, field
from typing import List

from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Track as TrackModel
from hmtc.schemas.video import VideoItem
from peewee import fn


@dataclass
class Album:
    id: int = None
    title: str = ""
    release_date: str = ""
    tracks: list = field(default_factory=list)

    def create_album(self):
        # this is being used by the settings temporary function at least, probably more
        # 10/14/24
        try:
            album = AlbumModel.create(
                title=self.title,
                release_date=self.release_date,
            )
            logger.info("Album created")
            return album
        except Exception as e:
            logger.error(e)
            logger.debug(f"Error creating album {self.title}. Skipping")

    def delete_album(self):
        logger.info(f"Deleting {self.title}")
        album_row = (
            AlbumModel.select().where(AlbumModel.video_id == self.video_id).first()
        )
        album_row.delete_instance()
        logger.info("Album deleted")

    @staticmethod
    def from_model(album):
        return Album(
            id=album.id,
            title=album.title,
            release_date=album.release_date,
            tracks=album.tracks,
        )

    def remove_track(self, id):
        try:
            track = TrackModel.get_by_id(id)
        except Exception as e:
            logger.error(e)
            logger.error(f"Track with id: {id} not found")
            return
        track_num = track.track_number

        track.delete_instance()
        for t in self.tracks:
            if t.track_number > track_num:
                t.track_number -= 1
                t.save()
        # if i was going to renumber them, it would take place here
        logger.info(f"Track {track.title} removed from {self.title}")

    def create_track(self, title, length):

        new_track_number = (
            TrackModel.select(fn.Count(TrackModel.id))
            .where(TrackModel.album_id == self.id)
            .scalar()
            + 1
        )
        track = TrackModel.create(
            title=title, album_id=self.id, track_number=new_track_number, length=length
        )
        logger.info(f"Track {track.title} created")
        return track
