from peewee import (
    SqliteDatabase,
    TextField,
    CharField,
    IntegerField,
    DateTimeField,
    Model,
    ForeignKeyField,
    DateField,
    AutoField,
    BooleanField,
)
from datetime import datetime
from hmtc.utils.youtube_functions import fetch_video_ids_from, download_video_info
from loguru import logger
import re

# used to init db in this file to avoid circular imports
db = SqliteDatabase(None)


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    deleted_at = DateTimeField(null=True)
    id = AutoField(primary_key=True)

    class Meta:
        database = db


class Series(BaseModel):
    name = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)


class Album(BaseModel):
    name = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)


class Video(BaseModel):
    youtube_id = CharField(unique=True)
    title = CharField()
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = CharField(null=True)

    private = BooleanField(default=False)
    error = BooleanField(default=False)
    error_info = CharField(null=True)

    series = ForeignKeyField(Series, backref="videos", null=True)

    def create_initial_section(self):
        if not self.sections:
            Section.create(
                start=0, end=self.duration, section_type="INITIAL", video=self
            )

    def add_section_break(self, timestamp):
        if timestamp in self.section_breaks:
            # logger.debug("Section Break already exists. Nothing to do")
            return
        old_section = self.get_section_with_timestamp(timestamp=timestamp)
        new_section = Section.create(
            start=timestamp,
            end=old_section.end,
            section_type=old_section.section_type,
            video=self,
        )
        old_section.end = timestamp
        old_section.save()

    def get_section_with_timestamp(self, timestamp):
        for sect in self.all_sections:
            if sect.is_timestamp_in_this_section(timestamp):
                return sect
        return None

    @classmethod
    def create_or_update(cls, youtube_id, series):
        existing = cls.get_or_none(Video.youtube_id == youtube_id)

        # this is where i should check for updated info
        # for now, once its in the database, not going to
        # auto-refresh the data.
        if not existing:
            video_info = download_video_info(youtube_id)
            if video_info["error"]:
                logger.error(f"{video_info['error_info']}")
                return None
            else:
                vid = Video.create(**video_info, series=series)
                vid.create_initial_section()
                vid.save()
                return vid
        else:
            logger.debug("Video already exists in DB. skipping update")
            return existing

    def update_episode_number(self, title, templates):
        for template in templates:
            match = re.search(template.template, title)
            if match:
                return match.group(1)

            return ""

    @property
    def section_breaks(self):
        breaks = set([])
        for sect in self.sections:
            breaks.add(sect.start)
            breaks.add(sect.end)
        return breaks

    def refresh_sections(self):
        self.sections = Section.select().join(Video).where(Section.video.id == self.id)

    @property
    def all_sections(self):
        self.refresh_sections()
        return sorted(self.sections, key=lambda x: x.start)

    @property
    def existing_files(self):
        return (
            File.select()
            .join(Video)
            .where(File.video.id == self.id and File.downloaded == True)
        )


class Playlist(BaseModel):
    name = CharField(unique=True)
    url = CharField(unique=True)

    # if the tracks from videos in this playlist
    # will be on the same album,
    # then APE should be False
    # example: Unreleased Omegle Bars
    album_per_episode = BooleanField(default=True)  # APE

    enabled = BooleanField(default=True)

    album = ForeignKeyField(Album, backref="playlist", null=True)
    series = ForeignKeyField(Series, backref="playlist", null=True)
    # last time playlist was checked for new videos

    last_update_completed = DateTimeField(null=True)

    def check_for_new_videos(self):

        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        ids = fetch_video_ids_from(self.url)
        logger.info(f"Found {len(ids)} videos in playlist {self.name}")
        for youtube_id in ids:
            vid = Video.create_or_update(youtube_id=youtube_id, series=self.series)
            if vid:
                vid.update_episode_number(vid.title, self.episode_number_templates)

        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()

    def __repr__(self):
        return f"Playlist({self.name=})"


class EpisodeNumberTemplate(BaseModel):
    playlist = ForeignKeyField(Playlist, backref="episode_number_templates")
    template = CharField()


class Track(BaseModel):
    title = CharField(null=True)
    track_number = CharField(null=True)
    album = ForeignKeyField(Album, backref="tracks", null=True)
    video = ForeignKeyField(Video, backref="tracks", null=True)
    start_time = IntegerField(null=True)
    length = IntegerField(null=True)
    end_time = IntegerField(null=True)
    words = CharField(null=True)
    notes = CharField(null=True)


class File(BaseModel):

    video = ForeignKeyField(Video, backref="files", null=True)
    track = ForeignKeyField(Track, backref="files", null=True)
    downloaded = BooleanField(default=False)
    skip_download = BooleanField(default=False)
    skip_reason = CharField(default="", null=True)
    error = BooleanField(default=False)
    error_info = CharField(null=True)
    local_path = CharField()
    filename = CharField(unique=True)
    extension = CharField()


def get_section_with_timestamp(video, timestamp):
    for sect in video.sections:
        if sect.is_timestamp_in_this_section(timestamp):
            return sect
    return None


class Section(BaseModel):
    start = IntegerField(null=True)
    end = IntegerField(null=True)
    video = ForeignKeyField(Video, backref="sections", null=True)
    section_type = CharField(null=True)

    def is_timestamp_in_this_section(self, timestamp):
        return timestamp > self.start and timestamp < self.end

    def __repr__(self):
        return (
            f"Section({self.start=}, {self.end=}, {self.video=}, {self.section_type})"
        )

    def __str__(self):
        return f"Section({self.id=}, {self.start=}, {self.end=}, {self.video=}, {self.section_type})"

    class Meta:
        indexes = (
            # Create a unique composite index on beat and track
            (("video", "start", "end"), True),
        )


class Artist(BaseModel):
    name = CharField()
    url = CharField(null=True)


class Beat(BaseModel):
    name = CharField()


class TrackBeat(BaseModel):
    beat = ForeignKeyField(Beat, backref="tracks")
    track = ForeignKeyField(Track, backref="beats")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and track
            (("beat", "track"), True),
        )


class BeatArtist(BaseModel):
    beat = ForeignKeyField(Beat, backref="artists")
    artist = ForeignKeyField(Artist, backref="beats")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("beat", "artist"), True),
        )


class User(BaseModel):
    username = CharField(max_length=80)
    email = CharField(max_length=120)

    def __str__(self):
        return self.username


class UserInfo(BaseModel):
    key = CharField(max_length=64)
    value = CharField(max_length=64)

    user = ForeignKeyField(User)

    def __str__(self):
        return f"{self.key} - {self.value}"


class Post(BaseModel):
    title = CharField(max_length=120)
    text = TextField(null=False)
    date = DateTimeField()

    user = ForeignKeyField(User)

    def __str__(self):
        return self.title
