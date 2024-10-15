from dataclasses import dataclass
from typing import List

from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Track as TrackModel
from hmtc.schemas.video import VideoItem


@dataclass
class Album:
    id: int = None
    title: str = ""
    release_date: str = ""
    # tracks: List[TrackItem]
    series: SeriesModel = None

    def create_album(self):
        # this is being used by the settings temporary function at least, probably more
        # 9/17/24
        try:
            AlbumModel.create(
                title=self.title,
                release_date=self.release_date,
                series=self.series,
            )
            logger.info("Album created")
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
