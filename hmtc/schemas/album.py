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
from hmtc.schemas.base import BaseItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.track import Track as TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.general import clean_filename


@dataclass(frozen=True, kw_only=True)
class Album(BaseItem):
    id: int = None
    item_type: str = "ALBUM"
    title: str = ""
    release_date: str = ""
    tracks: list = field(default_factory=list)
    video_ids: list = field(default_factory=list)
    videos: list = field(default_factory=list)
    files: list = field(default_factory=list)

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

    @staticmethod
    def from_model(album: AlbumModel) -> "Album":
        return Album(
            id=album.id,
            title=album.title,
            release_date=album.release_date,
            tracks=[TrackItem.from_model(x) for x in album.tracks],
            video_ids=[video.id for video in album.videos] if album.videos else [],
            videos=[VideoItem.from_model(video) for video in album.videos],
            files=[FileItem.from_model(f) for f in album.files],
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "release_date": str(self.release_date),
            "tracks": [track.serialize() for track in self.tracks],
            "video_ids": self.video_ids,
            "videos": [video.serialize() for video in self.videos],
        }

    @staticmethod
    def update_from_dict(item_id, new_data):
        album = AlbumModel.get_by_id(item_id)
        album.title = new_data["title"]
        album.release_date = new_data["release_date"]
        album.save()

    @staticmethod
    def delete_id(item_id):
        album = AlbumModel.get_by_id(item_id)
        for file in album.files:
            FileManager.delete_file(file)
        for track in album.tracks:
            for file in track.files:
                FileManager.delete_file(file)
            track.delete_instance()
        album.delete_instance()

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
            # Default Track title
            # its also defined in SectionSelector.vue

            topics_string = ", ".join([x.topic.text for x in section.topics])
            if len(topics_string) > 40:

                new_title = topics_string[:40] + "..."
            else:
                new_title = topics_string
        else:
            new_title = str(section.id) + video.title[:40]

        track = self.create_track(
            title=clean_filename(new_title), length=(section.end - section.start) / 1000
        )

        sect = SectionModel.get_by_id(section.id)
        sect.track = track
        sect.save()
        track_item = TrackItem.from_model(track)
        track_item.create_all_files(video)
        return track_item

    def use_video_poster(self, video: VideoItem = None):
        if video is None:
            video_poster = FileManager.get_file_for_video(
                video=self.videos[0], filetype="poster"
            )
        else:
            video_poster = FileManager.get_file_for_video(
                video=video, filetype="poster"
            )
        if video_poster is None:
            logger.error(f"No poster found. video args {video}.")
            return
        if video_poster.filename == "no-image.png":
            logger.error(f"Poster is the default poster. Not adding to album.")
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

    @staticmethod
    def delete_if_unused(album_id):
        album = AlbumModel.get_by_id(album_id)
        if album.videos.count() == 0 and album.tracks.count() == 0:
            album.delete_instance()
        else:
            logger.error(f"Album {album.title} has videos or tracks, cannot delete")

    @staticmethod
    def save_album(dict_of_items):
        item = dict_of_items["item"]
        edited_item = dict_of_items["editedItem"]
        logger.debug(f"Item received from Vue: {item}")

        try:
            album = AlbumModel.get_by_id(item["id"])
        except Exception:
            ## this should probably check item for id instead of edited_item
            logger.debug(f"Album ID not found. Creating {edited_item}")
            edited_item["id"] = None  # db should assign id
            album = AlbumModel.create(**edited_item)

        album.title = edited_item["title"]
        album.release_date = edited_item["release_date"]
        album.save()
