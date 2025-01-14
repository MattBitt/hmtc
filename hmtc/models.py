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
    DeferredForeignKey,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    TextField,
    fn,
)

from hmtc.config import init_config

db_null = PostgresqlDatabase(None)
config = init_config()
STORAGE = Path(config["STORAGE"])


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
        result = {}
        for col, column_type in cols.items():
            value = getattr(self, col)
            if isinstance(column_type, DateField) or isinstance(
                column_type, DateTimeField
            ):
                result[col] = value.isoformat()
            else:
                result[col] = value
        return result

    @classmethod
    def query_from_kwargs(cls, query=None, **kwargs):
        if query is None:
            query = cls.select()

        for key, value in kwargs.items():
            if key not in cls._meta.fields:
                raise ValueError(f"Field {key} not found in {cls.__name__}")
            query = query.where(getattr(cls, key) == value)
        return query

    @classmethod
    def order_by_kwargs(cls, query=None, **kwargs):
        if query is None:
            query = cls.select()

        for key, value in kwargs.items():
            if key not in cls._meta.fields:
                raise ValueError(f"Field {key} not found in {cls.__name__}")
            query = query.order_by(getattr(cls, key))
        return query

    class Meta:
        database = db_null


class Series(BaseModel):
    title = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)

    def __repr__(self):
        return f"SeriesModel({self.id} - {self.title})"

    def __str__(self):
        return f"SeriesModel({self.id} - {self.title})"


class Album(BaseModel):
    title = CharField(unique=True)
    release_date = DateField(null=True)

    def __repr__(self):
        return f"AlbumModel({self.id} - {self.title=})"

    def __str__(self):
        return f"AlbumModel({self.id} - {self.title=})"


class Disc(BaseModel):
    title = CharField()
    album = ForeignKeyField(Album, backref="discs")

    def __repr__(self):
        return f"DiscModel({self.id} - {self.disc_title=})"

    def __str__(self):
        return f"DiscModel({self.id} - {self.disc_title=})"


class Channel(BaseModel):
    title = CharField(unique=True)
    url = CharField()
    youtube_id = CharField(unique=True)
    last_update_completed = DateTimeField(default=datetime.now())
    auto_update = BooleanField(default=False)

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


class Video(BaseModel):
    description = TextField()
    duration = IntegerField()
    title = CharField()
    upload_date = DateField()
    url = CharField()
    youtube_id = CharField(unique=True)
    unique_content = BooleanField(default=False)

    # won't be assigned by jellyfin until after the video is uploaded
    jellyfin_id = CharField(null=True)

    # relationships
    channel = ForeignKeyField(Channel, backref="videos")
    disc = ForeignKeyField(Disc, backref="videos", null=True)

    def __repr__(self):
        return f"VideoModel({self.id} - {self.title=})"

    def __str__(self):
        return f"VideoModel({self.id} - {self.title=})"


class DiscVideo(BaseModel):
    video_id = ForeignKeyField(Video, backref="albums")
    disc_id = ForeignKeyField(Disc, backref="albums")
    order = IntegerField()


class YoutubeSeriesVideo(BaseModel):
    youtube_series = ForeignKeyField(YoutubeSeries, backref="video")
    video = ForeignKeyField(Video, backref="youtube_series")
    episode_number = IntegerField(null=True)
    episode_verbose = CharField(null=True)

    class Meta:
        indexes = ((("youtube_series", "video"), True),)

    def __repr__(self):
        return f"YoutubeSeriesVideoModel({self.id} - {self.youtube_series=})"

    def __str__(self):
        return f"YoutubeSeriesVideoModel({self.id} - {self.youtube_series=})"


class Section(BaseModel):
    start = IntegerField()
    end = IntegerField()
    section_type = CharField()

    video = ForeignKeyField(Video, backref="sections")

    def __repr__(self):
        return (
            f"SectionModel({self.id} - {self.start}:{self.end} - {self.section_type})"
        )

    def __str__(self):
        return f"SectionModel({self.id} - {self.section_type})"


class Topic(BaseModel):
    text = CharField()

    def __repr__(self):
        return f"TopicModel({self.id} - {self.text=})"

    def __str__(self):
        return f"TopicModel({self.id} - {self.text=})"


class SectionTopic(BaseModel):
    section = ForeignKeyField(Section, backref="topics")
    topic = ForeignKeyField(Topic, backref="sections")
    order = IntegerField()

    def __repr__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"

    def __str__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"


class Track(BaseModel):
    title = CharField()
    track_number = IntegerField()
    track_number_verbose = CharField(null=True)
    length = IntegerField()
    # won't be assigned by jellyfin until after the track is uploaded
    jellyfin_id = IntegerField(null=True)

    section = ForeignKeyField(Section, backref="track")
    disc = ForeignKeyField(Disc, backref="tracks")

    def __repr__(self):
        return f"TrackModel({self.id} - {self.title=})"

    def __str__(self):
        return f"TrackModel({self.id} - {self.title=})"


class User(BaseModel):
    username = CharField(max_length=80)
    email = CharField(max_length=120)
    hashed_password = CharField(max_length=255)
    jellyfin_id = CharField(null=True)

    def __repr__(self):
        return f"User({self.id} - {self.username=})"

    def __str__(self):
        return f"User({self.id} - {self.username=})"


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
        indexes = ((("beat", "track"), True),)


class BeatArtist(BaseModel):
    beat = ForeignKeyField(Beat, backref="artists")
    artist = ForeignKeyField(Artist, backref="beats")

    def __repr__(self):
        return f"BeatArtistModel({self.id} - {self.beat=} - {self.artist=})"

    def __str__(self):
        return f"BeatArtistModel({self.id} - {self.beat=} - {self.artist=})"

    class Meta:
        indexes = ((("beat", "artist"), True),)


class SuperchatSegment(BaseModel):
    # should probably use the Section as a base
    start_time_ms = IntegerField()
    end_time_ms = IntegerField()
    next_segment = ForeignKeyField("self", backref="previous_segment", null=True)

    # section is the 'output' of the segment to turn it into a track
    section = ForeignKeyField(Section, backref="superchat_segments", null=True)

    def __repr__(self):
        return f"SuperchatSegmentModel({self.id} - {self.start_time_ms}:{self.end_time_ms})"

    def __str__(self):
        return f"SuperchatSegmentModel({self.id} - {self.start_time_ms}:{self.end_time_ms})"


class Superchat(BaseModel):
    frame = IntegerField()

    video = ForeignKeyField(Video, backref="superchats")
    segment = ForeignKeyField(SuperchatSegment, backref="superchats", null=True)

    def __repr__(self):
        return f"SuperchatModel({self.id} - {self.frame=})"

    def __str__(self):
        return f"SuperchatModel({self.id} - {self.frame=})"

    class Meta:
        indexes = ((("frame", "video"), True),)


class File(BaseModel):
    path = CharField()
    file_size = IntegerField()  # stored in kbytes
    modified_datetime = DateTimeField()
    hash = CharField(null=True)  # could be useful for file verification

    def __repr__(self):
        return f"FileModel({self.id} - {self.path=})"

    def __str__(self):
        return f"FileModel({self.id} - {self.path=})"


class ImageFile(File):
    height = IntegerField()
    width = IntegerField()
    colorspace = CharField(null=True)  # e.g., RGB, CMYK, etc.

    def __repr__(self):
        return f"PosterFileModel({self.id} - {self.path=})"

    def __str__(self):
        return f"PosterFileModel({self.id} - {self.path=})"


class InfoFile(File):
    # Since this appears to be a basic info file, we might not need additional fields
    # The base File fields should be sufficient, but we'll keep the class for type distinction

    def __repr__(self):
        return f"InfoFileModel({self.id} - {self.path=})"

    def __str__(self):
        return f"InfoFileModel({self.id} - {self.path=})"


class SubtitleFile(File):
    def __repr__(self):
        return f"SubtitleFile({self.id} - {self.path=})"

    def __str__(self):
        return f"SubtitleFile({self.id} - {self.path=})"


class LyricFile(File):
    def __repr__(self):
        return f"LyricFile({self.id} - {self.path=})"

    def __str__(self):
        return f"LyricFile({self.id} - {self.path=})"


class AudioFile(File):
    bitrate = IntegerField()  # typically in kbps
    sample_rate = IntegerField()  # typically in Hz
    channels = IntegerField(default=2)  # mono=1, stereo=2, etc.
    duration = IntegerField()  # typically in seconds or milliseconds

    def __repr__(self):
        return f"AudioFileModel({self.id} - {self.path=})"

    def __str__(self):
        return f"AudioFileModel({self.id} - {self.path=})"


# moving pictures, not the entity
# ie mkv, avi files instead of a 'Video'
# from Youtube
class VideoFile(File):
    duration = IntegerField()  # in seconds or milliseconds
    fps = FloatField()  # e.g., 23.976, 29.97, 60
    width = IntegerField()
    height = IntegerField()
    codec = CharField(null=True)

    def __repr__(self):
        return f"VideoFileModel({self.id} - {self.path=})"

    def __str__(self):
        return f"VideoFileModel({self.id} - {self.path=})"


class TrackFiles(BaseModel):
    FILETYPES = ["info", "audio"]

    item = ForeignKeyField(Track, backref="files", unique=True)
    info = ForeignKeyField(InfoFile, null=True)
    audio = ForeignKeyField(AudioFile, null=True)


class AlbumFiles(BaseModel):
    FILETYPES = ["info", "poster"]
    item = ForeignKeyField(Album, backref="files", unique=True)
    info = ForeignKeyField(InfoFile, null=True)
    poster = ForeignKeyField(ImageFile, null=True)


# Entity Video not moving pictures
class VideoFiles(BaseModel):
    FILETYPES = ["info", "poster", "subtitle", "video", "audio"]
    PATH = STORAGE / "videos"

    item = ForeignKeyField(Video, backref="files", unique=True)
    info = ForeignKeyField(InfoFile, null=True)
    poster = ForeignKeyField(ImageFile, null=True)
    video = ForeignKeyField(VideoFile, null=True)
    audio = ForeignKeyField(AudioFile, null=True)
    subtitle = ForeignKeyField(SubtitleFile, null=True)


class ChannelFiles(BaseModel):
    FILETYPES = ["info", "poster"]
    PATH = STORAGE / "channels"
    item = ForeignKeyField(Channel, backref="files", unique=True)
    info = ForeignKeyField(InfoFile, null=True)
    poster = ForeignKeyField(ImageFile, null=True)


__all__ = [
    # ... existing entries ...
    "File",
    "ImageFile",
    "InfoFile",
    "AudioFile",
    "VideoFile",
    "Album",
    "AlbumFiles",
    "TrackFiles",
    "VideoFiles",
    "Artist",
    "Beat",
    "BeatArtist",
    "Channel",
    "ChannelFiles",
    "Disc",
    "DiscVideo",
    "Section",
    "SectionTopic",
    "Series",
    "Superchat",
    "SuperchatSegment",
    "Topic",
    "Track",
    "TrackBeat",
    "User",
    "Video",
    "YoutubeSeries",
    "YoutubeSeriesVideo",
    "File",
    "ImageFile",
    "InfoFile",
    "AudioFile",
    "VideoFile",
    "SubtitleFile",
    "LyricFile",
]
