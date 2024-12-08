import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import total_ordering
from pathlib import Path
from typing import List

from loguru import logger
from peewee import (
    AutoField,
    BlobField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    TextField,
    fn,
)

from hmtc.config import init_config
from hmtc.utils.general import clean_filename
from hmtc.utils.youtube_functions import fetch_ids_from

db_null = PostgresqlDatabase(None)

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])
VIDEO_MEDIA_PATH = STORAGE / "videos"

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH"))


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class BaseModel(Model):
    id = AutoField(primary_key=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()

        try:
            x = super(BaseModel, self).save(*args, **kwargs)
        except Exception as e:
            db_null.rollback()
            logger.error(f"Error saving model: {e}")
            raise e

        return x

    def my_dict(self):
        cols = self._meta.columns
        return {col: getattr(self, col) for col in cols}

    class Meta:
        database = db_null


class BaseFile(BaseModel):
    WORKING_PATH = WORKING / "uploads"

    path = CharField()
    filename = CharField()
    file_type = CharField()


class Series(BaseModel):
    title = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)

    def __repr__(self):
        return f"SeriesModel({self.id} - {self.title})"

    def __str__(self):
        return f"SeriesModel({self.id} - {self.title})"


class Channel(BaseModel):
    title = CharField(unique=True)
    url = CharField()
    youtube_id = CharField(unique=True)
    last_update_completed = DateTimeField(default=datetime.now())
    auto_update = BooleanField(default=False)

    def simple_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "youtube_id": self.youtube_id,
            "last_update_completed": str(self.last_update_completed),
            "auto_update": self.auto_update,
        }

    def __repr__(self):
        return f"ChannelModel({self.id} - {self.title=})"

    def __str__(self):
        return f"ChannelModel({self.id} - {self.title=})"


class YoutubeSeries(BaseModel):
    title = CharField(unique=True, max_length=120)
    series = ForeignKeyField(Series, backref="youtube_series")

    def __repr__(self):
        return f"YoutubeSeriesModel({self.id} - {self.title=})"

    def __str__(self):
        return f"YoutubeSeriesModel({self.id} - {self.title=})"


class Album(BaseModel):
    title = CharField(unique=True)
    release_date = DateField(null=True)

    def __repr__(self):
        return f"AlbumModel({self.id} - {self.title=})"

    def __str__(self):
        return f"AlbumModel({self.id} - {self.title=})"

    def simple_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_date": str(self.release_date),
        }

    @staticmethod
    def empty_dict():
        return {"id": 0, "title": "No Album", "release_date": "2021-01-01"}

    @staticmethod
    def new_track_number(album_id):
        return (
            Track.select(fn.Count(Track.id)).where(Track.album_id == album_id).scalar()
        ) + 1


class Video(BaseModel):
    youtube_id = CharField(unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = TextField(null=True)
    contains_unique_content = BooleanField(default=False)
    manually_edited = BooleanField(default=False)
    jellyfin_id = CharField(null=True, max_length=255)

    # relationships
    album = ForeignKeyField(Album, backref="videos", null=True)
    channel = ForeignKeyField(Channel, backref="videos", null=True)
    series = ForeignKeyField(Series, backref="videos", null=True)
    youtube_series = ForeignKeyField(YoutubeSeries, backref="videos", null=True)

    def __repr__(self):
        return f"VideoModel({self.id} - {self.title=})"

    def __str__(self):
        return f"VideoModel({self.id} - {self.title=})"


class Track(BaseModel):
    title = CharField()
    track_number = IntegerField(null=False)
    length = IntegerField(null=True)
    jellyfin_id = IntegerField(null=True)
    album = ForeignKeyField(Album, backref="tracks", null=True)

    def simple_dict(self):
        files = File.select().where(File.track_id == self.id)
        return {
            "id": self.id,
            "title": self.title,
            "track_number": self.track_number,
            "length": self.length,
            "files": [f.simple_dict() for f in files],
        }

    @staticmethod
    def empty_dict():
        return {
            "id": 0,
            "title": "No Track",
            "track_number": 0,
            "length": 0,
            "files": [],
        }

    def __repr__(self):
        return f"TrackModel({self.id} - {self.title=})"

    def __str__(self):
        return f"TrackModel({self.id} - {self.title=})"


class Section(BaseModel):
    start = IntegerField(null=True)
    end = IntegerField(null=True)
    section_type = CharField(null=True)
    is_first = BooleanField(default=False)
    is_last = BooleanField(default=False)
    ordinal = IntegerField(null=True)
    video = ForeignKeyField(Video, backref="sections", null=True)
    track = ForeignKeyField(Track, backref="section", null=True)

    def __repr__(self):
        return (
            f"SectionModel({self.id} - {self.start}:{self.end} - {self.section_type})"
        )

    def __str__(self):
        return f"SectionModel({self.id} - {self.section_type})"


class User(BaseModel):
    username = CharField(max_length=80)
    email = CharField(max_length=120)

    def __repr__(self):
        return f"User({self.id} - {self.username=})"

    def __str__(self):
        return f"User({self.id} - {self.username=})"


class FileType(BaseModel):
    title = CharField(unique=True)  # eg "info", "poster", "video", "audio", "image"

    def __repr__(self):
        return f"FileTypeModel({self.id} - {self.file_type=})"

    def __str__(self):
        return f"FileTypeModel({self.id} - {self.file_type=})"

    def simple_dict(self):
        return {
            "id": self.id,
            "title": self.title,
        }

    @staticmethod
    def empty_dict():
        return {
            "id": 0,
            "title": "No Title for File Type....",
        }


class File(BaseModel):
    filename = CharField(unique=True)
    file_type = ForeignKeyField(FileType, backref="files")
    # to be deprecated 12/4/24
    video = ForeignKeyField(Video, backref="files", null=True)
    album = ForeignKeyField(Album, backref="files", null=True)
    track = ForeignKeyField(Track, backref="files", null=True)

    def __repr__(self):
        return f"FileModel({self.id} - {self.filename=})"

    def __str__(self):
        return f"FileModel({self.id} - {self.filename=})"

    def simple_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
        }


class Artist(BaseModel):
    name = CharField()
    url = CharField(null=True)

    def __repr__(self):
        return f"ArtistModel({self.id} - {self.name=})"

    def __str__(self):
        return f"ArtistModel({self.id} - {self.name=})"


class Beat(BaseModel):
    title = CharField()

    def __repr__(self):
        return f"Beat({self.id} - {self.title=})"

    def __str__(self):
        return f"Beat({self.id} - {self.title=})"


class TrackBeat(BaseModel):
    beat = ForeignKeyField(Beat, backref="tracks")
    track = ForeignKeyField(Track, backref="beats")

    def __repr__(self):
        return f"TrackBeatModel({self.id} - {self.beat=} - {self.track=})"

    def __str__(self):
        return f"TrackBeatModel({self.id} - {self.beat=} - {self.track=})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and track
            (("beat", "track"), True),
        )


class BeatArtist(BaseModel):
    beat = ForeignKeyField(Beat, backref="artists")
    artist = ForeignKeyField(Artist, backref="beats")

    def __repr__(self):
        return f"BeatArtistModel({self.id} - {self.beat=} - {self.artist=})"

    def __str__(self):
        return f"BeatArtistModel({self.id} - {self.beat=} - {self.artist=})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("beat", "artist"), True),
        )


class Topic(BaseModel):
    text = CharField()

    def __repr__(self):
        return f"TopicModel({self.id} - {self.text=})"

    def __str__(self):
        return f"TopicModel({self.id} - {self.text=})"


class SectionTopics(BaseModel):
    section = ForeignKeyField(Section, backref="topics")
    topic = ForeignKeyField(Topic, backref="sections")
    order = IntegerField()

    def __repr__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"

    def __str__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"


class SuperchatSegment(BaseModel):
    start_time = IntegerField()
    end_time = IntegerField()
    next_segment: int = ForeignKeyField("self", backref="previous_segment", null=True)

    video = ForeignKeyField(Video, backref="superchats")
    section = ForeignKeyField(Section, backref="segment", null=True)

    def __repr__(self):
        return f"SuperchatSegmentModel({self.id} - {self.start_time}:{self.end_time})"

    def __str__(self):
        return f"SuperchatSegmentModel({self.id} - {self.start_time}:{self.end_time})"


class Superchat(BaseModel):
    frame_number = IntegerField()

    video = ForeignKeyField(Video, backref="superchats")
    segment = ForeignKeyField(SuperchatSegment, backref="superchats", null=True)

    def __repr__(self):
        return f"SuperchatModel({self.id} - {self.frame_number=})"

    def __str__(self):
        return f"SuperchatModel({self.id} - {self.frame_number=})"

    def simple_dict(self):
        return {
            "id": self.id,
            "frame_number": self.frame_number,
            "video_id": self.video.id,
            "superchat_segment_id": self.segment.id if self.segment else None,
        }

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("frame_number", "video"), True),
        )


class SuperchatFile(BaseFile):
    superchat_id: int = ForeignKeyField(Superchat, backref="files", null=True)
    segment_id: int = ForeignKeyField(SuperchatSegment, backref="files", null=True)


class Bird(BaseModel):
    species = CharField(unique=True)
    weight = IntegerField()
    color = CharField(null=True)

    def __repr__(self):
        return f"BirdModel({self.id} - {self.species=})"

    def __str__(self):
        return f"BirdModel({self.id} - {self.species=})"


class BirdFile(BaseModel):
    bird_id = ForeignKeyField(Bird, backref="files")
    file_type = ForeignKeyField(FileType, backref="files")
    filename = CharField()
    verified_on_disk = DateField(null=True)
    missing_from_disk = DateField(null=True)

    def __repr__(self):
        return f"BirdFileModel({self.bird_id} - {self.file_type=})"

    def __str__(self):
        return f"BirdFileModel({self.id} - {self.file_type=})"

    class Meta:
        indexes = (
            # Create a unique composite index
            (("bird_id", "file_type"), False),
        )


__all__ = [
    "Album",
    "Artist",
    "Beat",
    "BeatArtist",
    "Bird",
    "BirdFile",
    "Channel",
    "File",
    "FileType",
    "Section",
    "SectionTopics",
    "Series",
    "Superchat",
    "SuperchatFile",
    "SuperchatSegment",
    "Topic",
    "Track",
    "TrackBeat",
    "User",
    "Video",
    "YoutubeSeries",
]
