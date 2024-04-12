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
    IntegrityError,
)
from datetime import datetime
from hmtc.utils.youtube_functions import fetch_video_ids_from, download_video_info
from hmtc.utils.general import move_file
from hmtc.utils.image import convert_webp_to_png, convert_jpg_to_png
from loguru import logger
from pathlib import Path
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


class File(BaseModel):
    local_path = CharField()
    filename = CharField(unique=True)
    extension = CharField()

    def move_to(self, source, target):

        new_path = Path(target) / self.filename
        source.rename(new_path)
        self.local_path = new_path
        self.save()
        return self


class Series(BaseModel):
    name = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)


class Album(BaseModel):
    name = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)


class Playlist(BaseModel):
    name = CharField(unique=True)
    url = CharField(unique=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)
    album_per_episode = BooleanField(default=True)
    series = ForeignKeyField(Series, backref="playlist", null=True)

    def check_for_new_videos(self, download_path, media_path):

        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        ids = fetch_video_ids_from(self.url, download_path)
        logger.debug(f"Found {len(ids)} videos in playlist {self.name}")
        for youtube_id in ids:
            if not youtube_id in self.video_list:
                vid = Video.create_new(
                    youtube_id=youtube_id,
                    series=self.series,
                    playlist=self,
                    download_path=download_path,
                    media_path=media_path,
                )
            if vid:
                vid.update_episode_number(vid.title, self.episode_number_templates)

        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()

    def __repr__(self):
        return f"Playlist({self.name=})"

    @property
    def video_list(self):
        return (
            Playlist.select(Video.youtube_id)
            .join(PlaylistVideo)
            .join(Video)
            .where(PlaylistVideo.playlist.id == self.id)
        )


# example for self-referential many-to-many relationship
# class Person(Model):
#     name = TextField()

# class Follower(Model):
#     from_person = ForeignKeyField(Person, related_name='followers')
#     to_person = ForeignKeyField(Person, related_name='followed_by')


class Video(BaseModel):
    youtube_id = CharField(unique=True)
    title = CharField()
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = CharField(null=True)

    file_path = CharField()  # should be a relative path

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

    def add_file(self, file, file_type):

        new_path = self.file_path / (file.name)
        new_file = move_file(file, new_path)

        f = File.create(
            local_path=new_file.parent,
            filename=new_file.name,
            extension=new_file.suffix,
        )
        VideoFile.create(file=f, video=self, file_type=file_type)

    @classmethod
    def create_new(
        cls, youtube_id, series, playlist=None, download_path=".", media_path="."
    ):
        existing = cls.get_or_none(Video.youtube_id == youtube_id)

        if not existing:

            video_info, files = download_video_info(youtube_id, download_path)
            if video_info["error"]:
                logger.error(f"{video_info['error_info']}")
                return None
            else:
                new_path = Path(Path(media_path) / video_info["upload_date"][0:4])
                if not new_path.exists():
                    new_path.mkdir(parents=True, exist_ok=True)
                video_info["file_path"] = new_path
                vid = Video.create(**video_info, series=series)

                for downloaded_file in files:

                    ext = Path(downloaded_file).suffix
                    match ext:
                        case ".json":
                            filetype = "info"
                        case ".webp":
                            filetype = "poster"
                            downloaded_file = convert_webp_to_png(downloaded_file)
                        case ".jpg":
                            # downloaded_file = convert_jpg_to_png(downloaded_file)
                            filetype = "poster"
                        case ".png":
                            filetype = "poster"
                        case _:
                            logger.debug(f"filetype unknown {downloaded_file}")
                            filetype = "UNKNOWN"
                    vid.add_file(downloaded_file, filetype)
                vid.create_initial_section()
                vid.save()
                if playlist:
                    PlaylistVideo.create(video=vid, playlist=playlist)
                return vid
        else:
            try:
                pass
                # PlaylistVideo.create(video=existing, playlist=playlist)

            except IntegrityError:
                # logger.debug(
                #     "Video already exists in DB from this playlist. skipping update"
                # )
                pass

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

    @property
    def poster(self):
        for vf in self.files:
            if vf.file.filename.endswith(".png"):
                return Path(vf.file.local_path + "/" + vf.file.filename)
        return None

    def __repr__(self):
        return f"Video({self.title=})"


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


class PlaylistVideo(BaseModel):
    video = ForeignKeyField(Video, backref="playlists")
    playlist = ForeignKeyField(Playlist, backref="videos")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("video", "playlist"), True),
        )


class PlaylistAlbum(BaseModel):
    album = ForeignKeyField(Album, backref="playlists")
    playlist = ForeignKeyField(Playlist, backref="albums")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("album", "playlist"), True),
        )


class VideoFile(BaseModel):
    file = ForeignKeyField(File, backref="videos")
    video = ForeignKeyField(Video, backref="files")
    file_type = CharField(null=True)  # should probably be an enum

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("file", "video"), True),
        )


class SeriesFile(BaseModel):
    file = ForeignKeyField(File, backref="seriess")
    series = ForeignKeyField(Series, backref="files")
    file_type = CharField(null=True)  # should probably be an enum

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("file", "series"), True),
        )


class TrackFile(BaseModel):
    file = ForeignKeyField(File, backref="tracks")
    track = ForeignKeyField(Track, backref="files")
    file_type = CharField(null=True)  # should probably be an enum

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("file", "track"), True),
        )


class ArtistFile(BaseModel):
    file = ForeignKeyField(File, backref="artists")
    artist = ForeignKeyField(Artist, backref="files")
    file_type = CharField(null=True)  # should probably be an enum

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("file", "artist"), True),
        )


class AlbumFile(BaseModel):
    file = ForeignKeyField(File, backref="albums")
    album = ForeignKeyField(Artist, backref="files")
    file_type = CharField(null=True)  # should probably be an enum

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("file", "album"), True),
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
