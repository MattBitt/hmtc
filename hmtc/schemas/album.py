from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import peewee
from loguru import logger
from peewee import fn

from hmtc.models import Album as AlbumModel
from hmtc.models import File as FileModel
from hmtc.models import Section as SectionModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.track import TrackItem
from hmtc.schemas.video import VideoItem


@dataclass
class Album:
    id: int = None
    title: str = ""
    release_date: str = ""
    tracks: list = field(default_factory=list)
    video_ids: list = field(default_factory=list)
    videos: list = field(default_factory=list)

    def create_album(self):
        # i should create the folder here
        # then i should add the album metadata to that folder
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
    def from_model(album: AlbumModel) -> "Album":
        return Album(
            id=album.id,
            title=album.title,
            release_date=album.release_date,
            tracks=album.tracks,
            video_ids=[video.id for video in album.videos] if album.videos else [],
            videos=[VideoItem.from_model(video) for video in album.videos],
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

    def create_from_section(
        self, section: SectionItem, video: VideoItem
    ) -> "TrackItem":
        if len(section.topics) > 0:
            topics_string = ", ".join([x.topic.text for x in section.topics])
            if len(topics_string) > 40:
                # also defined in SectionCarousel.vue
                new_title = topics_string[:40] + "..."
            else:
                new_title = topics_string
        else:
            new_title = video.title[:40]

        track = self.create_track(
            title=new_title, length=(section.end - section.start) / 1000
        )
        track_item = TrackItem.from_model(track)

        sect = SectionModel.get_by_id(section.id)
        sect.track = track
        sect.save()

        return track_item

    def use_video_poster(self):

        try:
            video_poster = (
                FileModel.select()
                .where(
                    (FileModel.video_id == self.video_ids[0])
                    & (FileModel.file_type == "poster")
                )
                .get()
            )
        except Exception as e:
            logger.error(e)
            logger.error("Poster not found")
            return
        video_poster_path = Path(video_poster.path) / video_poster.filename
        logger.error(f"Video poster path: {video_poster_path}")
        file_item = FileItem.from_path(video_poster_path)
        file_item = file_item.make_a_temporary_copy()
        album_poster = FileManager.add_file_item_to_album(file=file_item, album=self)

        logger.info(f"Poster added to {album_poster}")

    def get_details_for_album_id(album_id: int) -> "Album":
        album = (
            AlbumModel.select(
                AlbumModel,
                VideoModel,
                TrackModel,
            )
            .join(
                VideoModel,
                peewee.JOIN.LEFT_OUTER,
                on=(AlbumModel.id == VideoModel.album_id),
            )
            .switch(AlbumModel)
            .join(
                TrackModel,
                peewee.JOIN.LEFT_OUTER,
                on=(AlbumModel.id == TrackModel.album_id),
            )
            .where(AlbumModel.id == album_id)
        ).get()
        return Album.from_model(album)
