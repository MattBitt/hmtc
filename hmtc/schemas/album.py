from dataclasses import dataclass
from typing import List

from loguru import logger

from hmtc.models import Album as AlbumModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Track as TrackModel
from hmtc.schemas.video import VideoItem

# # not sure what this is for
# # don't think it's used
# @dataclass
# class TrackItem:
#     title: str
#     track_number: int
#     duration: int
#     album_id: int = None
#     id: int = None


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

    # @staticmethod
    # def grab_for_video(video_id: int):
    #     if not video_id:
    #         raise ValueError("Video object is required")

    #     try:
    #         album = AlbumModel.select().where(AlbumModel.video_id == video_id).first()
    #         # logger.info(f"Album grabbed {album.title}")
    #     except Exception as e:
    #         logger.error(e)
    #         album = None
    #         logger.error(f"No album found for video {video_id}")
    #     if album:
    #         return Album(video_id=album.video_id, title=album.title, tracks=[])
    #     else:
    #         return None

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

    # @staticmethod
    # def update_album(title, video_id):
    #     if not video_id:
    #         raise ValueError("Video object is required")
    #     if title == "":
    #         raise ValueError("Title is required")

    #     album = AlbumModel.select().where(AlbumModel.video_id == video_id).first()
    #     album.title = title
    #     album.save()

    # @staticmethod
    # def get_next_track_number(album: "Album"):
    #     if not album:
    #         raise ValueError("Album object is required")
    #     t = TrackModel.select().where(TrackModel.album_id == album.id).count()
    #     return t + 1
