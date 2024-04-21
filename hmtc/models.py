import os
from peewee import (
    PostgresqlDatabase,
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
from hmtc.utils.youtube_functions import (
    fetch_video_ids_from,
    download_video_info_from_id,
    download_media_files,
)
from hmtc.utils.general import move_file
from hmtc.utils.image import convert_webp_to_png
from loguru import logger
from pathlib import Path
import re

from hmtc.config import init_config

config = init_config()

db_name = config.get("DATABASE", "NAME")
user = config.get("DATABASE", "USER")
password = config.get("DATABASE", "PASSWORD")
host = config.get("DATABASE", "HOST")
port = config.get("DATABASE", "PORT")


db = PostgresqlDatabase(db_name, user=user, password=password, host=host, port=port)
db.connect()


def get_file_type(file):
    try:
        f = Path(file.local_path) / file.filename
    except AttributeError:
        f = file
    ext = f.suffix
    if ext in [".mkv", ".mp4", ".webm"]:
        filetype = "video"
    elif ext in [".mp3", ".wav"]:
        filetype = "audio"
    elif ext in [".srt", ".vtt"]:
        filetype = "subtitle"
    elif ext in [".nfo", ".info.json", ".json"]:
        filetype = "info"
    elif ext in [".jpg", ".jpeg", ".png"]:

        filetype = "image"
    elif ext == ".webp":
        raise ValueError("Webp files should be converted to png")
    else:
        raise ValueError(f"Unknown file type: {f}")
    return filetype


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

    @classmethod
    def add_to_db(cls, file):
        existing = cls.get_or_none(File.filename == file.name)
        if not existing:
            f = File.create(
                local_path=file.parent, filename=file.name, extension=file.suffix
            )
            return f
        else:
            return existing


class Series(BaseModel):
    name = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)

    @property
    def enabled_videos(self):
        return self.videos.where(Video.enabled == True).count()

    @property
    def total_videos(self):
        return self.videos.count()


class Album(BaseModel):
    name = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)


class Channel(BaseModel):
    name = CharField(unique=True)
    url = CharField(unique=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)

    def check_for_new_videos(self):
        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        ids = fetch_video_ids_from(self.url)
        for id in ids:
            try:
                ChannelVideo.create(youtube_id=id, channel=self)
            except IntegrityError:
                continue

        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.debug(f"Finished updating channel {self.name}")

    @property
    def num_videos(self):
        return self.channel_vids.count()


class ChannelVideo(BaseModel):
    # This shouldn't be confused with regular videos
    # This is a list of videos that are on a channel
    # I will use this to figure out what videos are missing
    # they don't appear on a playlist
    youtube_id = CharField(unique=True)
    channel = ForeignKeyField(Channel, backref="channel_vids", null=True)


class Playlist(BaseModel):
    name = CharField(unique=True)
    url = CharField(unique=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)
    album_per_episode = BooleanField(default=True)
    series = ForeignKeyField(Series, backref="playlists", null=True)
    channel = ForeignKeyField(Channel, backref="playlists", null=True)
    add_videos_enabled = BooleanField(default=True)

    def check_for_new_videos(self):
        download_path = config.get("GENERAL", "DOWNLOAD_PATH")

        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        ids = fetch_video_ids_from(self.url, download_path)
        logger.debug(f"Found {len(ids)} videos in playlist {self.name}")
        for youtube_id in ids:
            vid = Video.create_from_yt_id(
                youtube_id=youtube_id,
                series=self.series,
                playlist=self,
                enabled=self.add_videos_enabled,
            )
            if vid:
                vid.update_episode_number(vid.title, self.episode_number_templates)

        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.success("Finished updating playlist {self.name}")

    def __repr__(self):
        return f"Playlist({self.name=})"

    # @property
    # def video_list(self):
    #     return (
    #         Playlist.select(Video.youtube_id)
    #         .join(PlaylistVideo)
    #         .join(Video)
    #         .where(PlaylistVideo.playlist.id == self.id)
    #     )

    # @property
    # def num_videos(self):
    #     return self.videos.count()


# example for self-referential many-to-many relationship
# class Person(Model):
#     name = TextField()

# class Follower(Model):
#     from_person = ForeignKeyField(Person, related_name='followers')
#     to_person = ForeignKeyField(Person, related_name='followed_by')


def process_downloaded_files(video, files):
    for downloaded_file in files:
        ext = downloaded_file.suffix
        if ext == ".webp":
            converted = convert_webp_to_png(downloaded_file)
            Path(downloaded_file).unlink()
            files.pop(files.index(downloaded_file))
            files.append(converted)
            ext = ".png"
            downloaded_file = converted

        existing = (
            File.select().where(File.filename == downloaded_file.name).get_or_none()
        )
        if not existing:
            if "webp" in downloaded_file.name:
                raise ValueError("asdfWebp files should be converted to png")
            video.add_file(downloaded_file)
            video.save()

    # return video, files


class Video(BaseModel):
    youtube_id = CharField(unique=True)
    title = CharField()
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = TextField(null=True)

    file_path = CharField()  # should be a relative path
    enabled = BooleanField(default=True)
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

    def add_file(self, file, file_type=None):

        new_path = Path(self.file_path) / (file.name)

        new_file = move_file(file, new_path)
        if new_file == "":
            logger.error(f"Error moving file {file} to {new_path}")
            return

        existing = File.select().where(
            (File.filename == new_file.name)
            & (File.local_path == new_file.parent)
            & (new_file.suffix == File.extension)
        )
        if existing:
            return existing

        if file_type is None:
            file_type = get_file_type(new_file)

        f = File.create(
            local_path=new_file.parent,
            filename=new_file.name,
            extension=new_file.suffix,
        )
        VideoFile.create(file=f, video=self, file_type=file_type)
        return f

    @classmethod
    def create_from_yt_id(cls, youtube_id, series, playlist=None, enabled=None):
        existing = cls.select().where(cls.youtube_id == youtube_id)
        if existing:
            # logger.debug(
            #     "Tried to create a video that already exists in database 🟡🟡🟡"
            # )
            return None

        info, files = cls.download_video_info(youtube_id)
        if info is None:
            logger.error(f"Error downloading video info for {youtube_id}")
            return None

        vid = cls.create(**info, series=series)

        process_downloaded_files(vid, files)

        vid.refresh_video_info()

        vid.create_initial_section()

        vid.save()

        if playlist:
            PlaylistVideo.create(video=vid, playlist=playlist)

        return vid

    def download_video_info(self, youtube_id):
        download_path = config.get("GENERAL", "DOWNLOAD_PATH")
        media_path = config.get("MEDIA", "VIDEO_PATH")

        thumbnail = not self.has_poster
        subtitle = not self.has_subtitle
        info = not self.has_info

        if not (thumbnail or subtitle or info):
            # logger.debug("All files already downloaded")
            return "", []

        video_info, files = download_video_info_from_id(
            youtube_id, download_path, thumbnail=thumbnail, subtitle=subtitle, info=info
        )
        if video_info["error"] or files is None:
            logger.error(f"{video_info['error_info']}")
            return None, None
        else:
            new_path = Path(Path(media_path) / video_info["upload_date"][0:4])
            if not new_path.exists():
                new_path.mkdir(parents=True, exist_ok=True)

            video_info["file_path"] = new_path
            return video_info, files

    def update_episode_number(self, title, templates):
        for template in templates:
            match = re.search(template.template, title)
            if match:
                return match.group(1)

            return ""

    def refresh_video_info(self):
        # for file in self.files:
        #     logger.debug(f"Processing file {file.file.filename} for video {self.title}")

        info, files = self.download_video_info(
            self.youtube_id,
        )
        if info and files:
            process_downloaded_files(self, files)

            self.title = info["title"]
            self.upload_date = info["upload_date"]
            self.duration = info["duration"]
            self.description = info["description"]
            self.save()

    def download_video(self):
        download_path = config.get("GENERAL", "DOWNLOAD_PATH")
        if self.has_video:
            logger.debug(
                "Video already downloaded. Delete it from the folder to redownload"
            )
            return
        result, files = download_media_files(self.youtube_id, download_path)
        if result:
            for file in files:
                self.add_file(file)

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
    def num_sections(self):
        return len(self.all_sections)

    def __repr__(self):
        return f"Video({self.title=})"

    @property
    def num_files(self):
        return len(self.existing_files)

    @property
    def poster(self):

        vf = (
            VideoFile.select(File.filename)
            .join(File)
            .where((VideoFile.video_id == self.id) & (VideoFile.file_type == "image"))
        ).get_or_none()
        path = Path(config.get("MEDIA", "VIDEO_PATH"))
        if vf:
            return path / vf.file.filename[:4] / vf.file.filename

        return ""

    @property
    def has_video(self):
        return self.files.where(VideoFile.file_type == "video").count() > 0

    @property
    def has_audio(self):
        return self.files.where(VideoFile.file_type == "audio").count() > 0

    @property
    def has_subtitle(self):
        return self.files.where(VideoFile.file_type == "subtitle").count() > 0

    @property
    def has_info(self):
        return self.files.where(VideoFile.file_type == "info").count() > 0

    @property
    def has_poster(self):
        return self.files.where(VideoFile.file_type == "image").count() > 0

    @property
    def upload_date_str(self):
        return self.upload_date.strftime("%Y%m%d")

    def extract_audio(self):
        if not self.has_video:
            logger.error(f"No video file found for {self.title}")
            return

        video_file = (
            VideoFile.select(File)
            .join(File)
            .where((VideoFile.video_id == self.id) & (VideoFile.file_type == "video"))
        ).get()
        path = Path(video_file.file.local_path)
        vf = path / video_file.file.filename
        af = path / f"{self.upload_date_str}___{self.youtube_id}.mp3"

        command = f"ffmpeg -i {vf} -vn -acodec libmp3lame -y {af}"
        logger.debug(f"Running command: {command}")
        os.system(command)

        self.add_file(af, file_type="audio")


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


def add_files_to_db():
    # this will add existing media files to the database
    media_path = Path("/mnt/c/DATA/hmtc_files/media")
    for mp in media_path.rglob("*"):
        if mp.is_file() and mp.stem[4] == "-":
            # currently date is in YYYY-MM-DD format
            # need to replace with YYYYMMDD
            new_name = mp.name.replace("-", "")
            mp = mp.rename(mp.parent / new_name)

        existing = File.select().where(
            (File.filename == mp.name)
            & (File.local_path == mp.parent)
            & (File.extension == mp.suffix)
        )
        if not existing:
            f = File.create(
                local_path=mp.parent,
                filename=mp.name,
                extension=mp.suffix,
            )


def create_video_file_associations():
    videos = Video.select()
    for vid in videos:
        files = File.select().where(File.filename.contains(vid.youtube_id))
        for file in files:
            VideoFile.create(file=file, video=vid, file_type=get_file_type(file))


if __name__ == "__main__":
    # add_files_to_db()
    create_video_file_associations()
