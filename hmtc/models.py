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


class Album(BaseModel):
    title = CharField(unique=True)
    release_date = DateField(null=True)

    def __repr__(self):
        return f"AlbumModel({self.id} - {self.title=})"

    def __str__(self):
        return f"AlbumModel({self.id} - {self.title=})"


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


class YoutubeSeriesVideo(BaseModel):
    youtube_series = ForeignKeyField(YoutubeSeries, backref="videos")
    video = DeferredForeignKey("Video", backref="youtube_series")
    episode_number = IntegerField(null=True)
    episode_verbose = CharField(null=True)

    def __repr__(self):
        return f"YoutubeSeriesVideoModel({self.id} - {self.youtube_series=})"

    def __str__(self):
        return f"YoutubeSeriesVideoModel({self.id} - {self.youtube_series=})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("youtube_series", "video"), True),
        )


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

    def __repr__(self):
        return f"VideoModel({self.id} - {self.title=})"

    def __str__(self):
        return f"VideoModel({self.id} - {self.title=})"


class Section(BaseModel):
    start = IntegerField()
    end = IntegerField()
    section_type = CharField()
    next_section = ForeignKeyField("self", backref="previous_section", null=True)
    video = ForeignKeyField(Video, backref="sections")

    def __repr__(self):
        return (
            f"SectionModel({self.id} - {self.start}:{self.end} - {self.section_type})"
        )

    def __str__(self):
        return f"SectionModel({self.id} - {self.section_type})"


class Track(BaseModel):
    title = CharField()
    track_number = IntegerField()
    length = IntegerField()

    # won't be assigned by jellyfin until after the track is uploaded
    jellyfin_id = IntegerField(null=True)

    section = ForeignKeyField(Section, backref="track")

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


class SectionTopic(BaseModel):
    section = ForeignKeyField(Section, backref="topics")
    topic = ForeignKeyField(Topic, backref="sections")
    order = IntegerField()

    def __repr__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"

    def __str__(self):
        return f"SectionTopicsModel({self.id} - {self.section=})"


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
        indexes = (
            # Create a unique composite index on beat and Artist
            (("frame", "video"), True),
        )


class AlbumVideo(BaseModel):
    album = ForeignKeyField(Album, backref="videos")
    video = ForeignKeyField(Video, backref="albums")
    disc_number = IntegerField()
    disc_number_verbose = CharField(null=True)

    def __repr__(self):
        return f"AlbumVideoModel({self.id} - {self.album=})"

    def __str__(self):
        return f"AlbumVideoModel({self.id} - {self.album=})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("album", "video"), True),
        )


class AlbumTrack(BaseModel):
    album = ForeignKeyField(Album, backref="tracks")
    track = ForeignKeyField(Track, backref="albums")
    track_number = IntegerField()
    track_number_verbose = CharField(null=True)

    def __repr__(self):
        return f"AlbumTracksModel({self.id} - {self.album=})"

    def __str__(self):
        return f"AlbumTracksModel({self.id} - {self.album=})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("album", "track"), True),
        )


__all__ = [
    "Album",
    "Artist",
    "Beat",
    "BeatArtist",
    "Channel",
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
    "AlbumVideo",
    "AlbumTrack",
]
