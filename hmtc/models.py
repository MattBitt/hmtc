import json
import os
from datetime import datetime, timedelta
from functools import total_ordering
from pathlib import Path

from loguru import logger
from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
    TextField,
)

from hmtc.config import init_config
from hmtc.utils.general import clean_filename, my_move_file
from hmtc.utils.youtube_functions import fetch_ids_from

db_null = PostgresqlDatabase(None)

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])
VIDEO_MEDIA_PATH = STORAGE / "videos"

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH"))


def create_hms_dict(seconds):
    # created on 9/10/24
    # used by sections page for input and
    # label (seconds in milliseconds)

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return dict(
        hour=h,
        minute=m,
        second=s,
    )


def get_file_type(file: str, override=None):
    if override is not None:
        return override

    logger.debug(f"File = {file}")
    f = Path(file)
    logger.debug(f"Path object {f}")

    ext = "".join(f.suffixes)

    logger.debug(f"Getting file type for {file} ext = {ext}")

    if ext in [".mkv", ".mp4", ".webm"]:
        filetype = "video"
    elif ext in [".mp3", ".wav"]:
        filetype = "audio"
    elif ext in [".srt", ".en.vtt"]:
        filetype = "subtitle"
    elif ext in [".nfo", ".info.json", ".json"]:
        filetype = "info"
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        filetype = "poster"
    else:
        logger.error(f"Unknown file type: file: {file} ext: {ext}")
        filetype = "unknown"

    return filetype


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class BaseModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    deleted_at = DateTimeField(null=True)
    id = AutoField(primary_key=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    def my_delete_instance(self, *args, **kwargs):
        # ignore this for now
        # self.deleted_at = datetime.now()
        # self.save()
        super(BaseModel, self).delete_instance(*args, **kwargs, recursive=True)
        return None

    def _poster(self, id):
        query = File.select().where(File.file_type == "poster")

        match type(self).__name__:
            case "Channel":
                return query.where(File.channel_id == id).get_or_none()
            case "Playlist":
                return query.where(File.playlist_id == id).get_or_none()
            case "Video":
                return query.where(File.video_id == id).get_or_none()
            case "Series":
                return query.where(File.series_id == id).get_or_none()

    @classmethod
    def active(cls):
        return cls.select().where(cls.deleted_at.is_null()).distinct()

    class Meta:
        database = db_null


class TodoTable(BaseModel):
    text: str = CharField()
    done: bool = BooleanField(default=False)

    def __str__(self):
        return f"TodoTable {self.text} - {self.done}"


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Series(BaseModel):
    MEDIA_PATH = STORAGE / "series"

    name = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.name.lower()) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, series=self
        )

    @property
    def poster(self):
        p = self._poster(self.id)
        if p:
            return p.file_string
        return None

    @property
    def enabled_videos(self):
        return self.videos.where(Video.enabled == True).count()

    @property
    def total_videos(self):
        return self.videos.count()

    @property
    def unique_videos(self):
        return self.videos.select().where(Video.contains_unique_content == True).count()

    def __repr__(self):
        return f"Series({self.name})"

    def __str__(self):
        return f"Series({self.name})"

    # used to serialize model to dict for vue
    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "name": self.name,
            "start_date": (self.start_date.isoformat() if self.start_date else None),
            "end_date": (self.end_date.isoformat() if self.end_date else None),
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Channel(BaseModel):
    MEDIA_PATH = STORAGE / "channels"

    name = CharField(null=True)
    url = CharField(null=True)
    youtube_id = CharField()
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)

    def check_for_new_videos(self):
        # this should be deprecated
        ids = fetch_ids_from(self.url)
        for youtube_id in ids:
            vid, created = Video.get_or_create(youtube_id=youtube_id, channel=self)
            # if not created:
            #     vid.channel = self
            #     vid.save()
        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.debug(f"Finished updating channel {self.name}")

    def grab_ids(self):
        return fetch_ids_from(self.url)

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.name.lower()) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, channel=self
        )

    def check_for_new_playlists(self):
        ids = fetch_ids_from(self.url + "/playlists")
        for youtube_id in ids:
            if youtube_id == "":
                logger.error("No youtube ID found")
            else:
                Playlist.create_from_yt_id(youtube_id=youtube_id, channel=self)
        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.debug(f"Finished updating channel {self.name}")

    def load_from_info_file(self):
        if self.info is None:
            logger.error(f"No info file found for channel {self.name}")
            return
        with open(self.info.filename, "r") as info_file:
            info = json.load(info_file)
            self.name = info["channel"]
            self.url = info["webpage_url"]
            self.youtube_id = info["id"]
            self.save()

    @property
    def num_videos(self):
        return self.videos.count()

    @property
    def poster(self):
        p = self._poster(self.id)
        if p:
            return p.file_string
        return None

    @property
    def info(self):
        logger.debug(f"Getting info for channel {self.name}")
        i = (
            File.select()
            .where(File.file_type == "info")
            .where(File.channel_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if i:
            return i
        return None

    # used to serialize model to dict for vue
    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "youtube_id": self.youtube_id,
            "url": self.url,
            "name": self.name,
            "enabled": self.enabled,
            "last_update_completed": (
                self.last_update_completed.isoformat()
                if self.last_update_completed
                else None
            ),
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Playlist(BaseModel):
    MEDIA_PATH = STORAGE / "playlists"

    title = CharField(default="Untitled")
    url = CharField(unique=True, null=True)
    youtube_id = CharField(unique=True, null=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)
    album_per_episode = BooleanField(default=True)
    enable_video_downloads = BooleanField(default=True)
    has_chapters = BooleanField(default=False)

    # if it doesn't contain unique content, it should probably
    # point to the original
    # eg Omegle Bars Clip 91.4 should point to the original Omegle Bars Clip 91
    # Omegle Bars Clip media would not be downloaded
    contains_unique_content = BooleanField(default=False)

    series = ForeignKeyField(Series, backref="playlists", null=True)
    channel = ForeignKeyField(Channel, backref="playlists", null=True)

    def load_info(self):
        logger.error("Deprecated: Playlist.load_info")
        return

    @classmethod
    def create_from_youtube_id(cls, youtube_id=None, channel=None):
        if youtube_id is None or youtube_id == "":
            logger.error("No youtube ID")
            return None

        info, files = cls.download_playlist_info(youtube_id)
        if info is None:
            logger.error(f"Error downloading video info for {youtube_id}")
            return None

        return cls.create(**info, channel=channel)

    @classmethod
    def download_playlist_info(
        cls, youtube_id=None, thumbnail=True, subtitle=True, info=True
    ):
        def download_playlist_info_from_id(*args, **kwargs):
            logger.error("Deprecated download_playlist_info ... from_id")
            return None

        logger.error("This function can't work anymore.... need to fix")
        return
        download_path = config.get("PATHS", "DOWNLOAD")
        media_path = config.get("PATHS", "MEDIA")
        playlist_info, files = download_playlist_info_from_id(
            youtube_id, download_path, thumbnail=thumbnail, subtitle=subtitle, info=info
        )
        if playlist_info["error"] or files is None:
            logger.error(f"{playlist_info['error_info']}")
            return None, None
        else:
            new_path = Path(Path(media_path) / playlist_info["upload_date"][0:4])
            if not new_path.exists():
                new_path.mkdir(parents=True, exist_ok=True)

            playlist_info["file_path"] = new_path
            return playlist_info, files

    def get_video_list_from_yt(self):
        download_path = WORKING / "downloads"
        ids = fetch_ids_from(self.url, download_path)
        return ids

    def update_videos_with_playlist_info(self):
        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        # also create any videos that don't exist
        # what about videos from other channels?
        # not going to track that yet. maybe one day.
        ids = self.get_video_list_from_yt()

        logger.debug(f"Found {len(ids)} videos in playlist {self.title}")

        for youtube_id in ids:
            if youtube_id == "":
                logger.error("No youtube ID")
            else:
                vid, created = Video.get_or_create(
                    youtube_id=youtube_id,
                )
                if vid:
                    vid.playlist = self
                    if vid.playlist.series:
                        vid.series = vid.playlist.series
                    vid.enabled = self.enable_video_downloads
                    vid.contains_unique_content = self.contains_unique_content
                    vid.save()

        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.success(f"Finished updating playlist {self.title}")

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.title.lower()) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, playlist=self
        )

    @property
    def poster(self):
        p = self._poster(self.id)
        if p:
            return p.file_string
        return None

    @property
    def info(self):
        logger.debug(f"Getting info file for playlist {self.title}")
        i = (
            File.select()
            .where(File.file_type == "info")
            .where(File.playlist_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if i:
            return i
        return None

    @property
    def has_poster(self):
        logger.error("I think this function is disabled too")
        return

    def apply_to_videos(self):
        vids = Video.select().where(Video.playlist_id == self.id)
        for vid in vids:
            vid.contains_unique_content = self.contains_unique_content
            vid.has_chapters = self.has_chapters
            vid.save()

    def __repr__(self):
        return f"Playlist({self.title})"

    # used to serialize model to dict for vue
    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "youtube_id": self.youtube_id,
            "url": self.url,
            "title": self.title,
            "enabled": self.enabled,
            "last_update_completed": (
                self.last_update_completed.isoformat()
                if self.last_update_completed
                else None
            ),
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class YoutubeSeries(BaseModel):
    title = CharField(unique=True, max_length=120)
    series = ForeignKeyField(Series, backref="youtube_series", null=True)

    def __repr__(self):
        return f"YoutubeSeriesModel({self.title=})"

    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            "series": self.series.name if self.series else None,
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Video(BaseModel):
    youtube_id = CharField(unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = TextField(null=True)
    enabled = BooleanField(default=True)
    private = BooleanField(default=False)
    contains_unique_content = BooleanField(default=True)
    has_chapters = BooleanField(default=False)
    manually_edited = BooleanField(default=False)
    jellyfin_id = CharField(null=True, max_length=255)
    channel = ForeignKeyField(Channel, backref="videos", null=True)
    series = ForeignKeyField(Series, backref="videos", null=True)
    playlist = ForeignKeyField(Playlist, backref="videos", null=True)
    youtube_series = ForeignKeyField(YoutubeSeries, backref="videos", null=True)

    def __repr__(self):
        return f"VideoModel({self.title=})"

    # used to serialize model to dict for vue
    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "youtube_id": self.youtube_id,
            "url": self.url,
            "title": self.title,
            "episode": self.episode,
            "upload_date": self.upload_date.isoformat(),
            "duration": self.duration,
            "description": self.description,
            "enabled": self.enabled,
            "private": self.private,
            "contains_unique_content": self.contains_unique_content,
            "has_chapters": self.has_chapters,
            "manually_edited": self.manually_edited,
            "jellyfin_id": self.jellyfin_id,
            "channel_name": self.channel.name if self.channel else None,
            "series_name": self.series.name if self.series else None,
            "playlist_title": self.playlist.title if self.playlist else None,
            "youtube_series_title": (
                self.youtube_series.title if self.youtube_series else None
            ),
            "album_title": self.album.title if self.album else None,
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class EpisodeNumberTemplate(BaseModel):
    playlist = ForeignKeyField(Playlist, backref="episode_number_templates")
    template = CharField()


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Section(BaseModel):
    start = IntegerField(null=True)
    end = IntegerField(null=True)
    section_type = CharField(null=True)
    is_first = BooleanField(default=False)
    is_last = BooleanField(default=False)
    next_section = ForeignKeyField("self", backref="previous_section", null=True)

    video = ForeignKeyField(Video, backref="sections", null=True)
    ordinal = IntegerField(null=True)

    @classmethod
    def create_initial_section(cls, video):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 09-10-24")
        return Section.create(
            start=0,
            end=video.duration,
            section_type="INITIAL",
            video=video,
            ordinal=1,
            is_first=True,
            is_last=True,
        )

    @classmethod
    def create_from_item(cls, item):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 09-10-24")
        return cls.create(
            start=item.start,
            end=item.end,
            section_type=item.section_type,
            video=item.video,
            ordinal=item.ordinal,
        )

    def is_timestamp_in_this_section(self, timestamp):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 09-10-24")
        return timestamp > self.start and timestamp < self.end

    def __repr__(self):
        return f"Section({self.id} - {self.start}:{self.end} - {self.section_type})"

    def __str__(self):
        return f"Section(id={self.id}, start={self.start}, end={self.end},type={self.section_type})"

    def find_both_sections(self, timestamp):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 8-31-24")
        before, after = None, None
        for sect in self.all_sections:
            if sect.start == timestamp:
                after = sect
            if sect.end == timestamp:
                before = sect

        return before, after

    @property
    def all_sections(self):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 8-31-24")
        return sorted(self.video.sections, key=lambda x: x.start)

    @property
    def num_sections(self):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 8-31-24")
        return len(self.all_sections)

    @property
    def oldbreakpoints(self):
        logger.debug("Is this used 🧪🧪🧪🧪🧪 8-31-24")
        breaks = set([])
        for sect in self.sections:
            breaks.add(sect.start)
            breaks.add(sect.end)
        return breaks

    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "start_dict": create_hms_dict(self.start / 1000),
            "end_dict": create_hms_dict(self.end / 1000),
            "start_string": str(timedelta(seconds=self.start / 1000)),
            "end_string": str(timedelta(seconds=self.end / 1000)),
            "duration": (self.end - self.start) / 1000,
            "section_type": self.section_type,
            "video_id": self.video.id if self.video else None,
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class User(BaseModel):
    username = CharField(max_length=80)
    email = CharField(max_length=120)

    def __str__(self):
        return self.username


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class UserInfo(BaseModel):
    key = CharField(max_length=64)
    value = CharField(max_length=64)

    user = ForeignKeyField(User)

    def __str__(self):
        return f"{self.key} - {self.value}"


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Post(BaseModel):
    title = CharField(max_length=120)
    text = TextField(null=False)
    date = DateTimeField()

    user = ForeignKeyField(User)

    def __str__(self):
        return self.title


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class File(BaseModel):
    WORKING_PATH = WORKING / "uploads"

    path = CharField(null=True)
    filename = CharField()
    extension = CharField(null=True)
    file_type = CharField(null=True)
    channel = ForeignKeyField(Channel, backref="files", null=True)
    series = ForeignKeyField(Series, backref="files", null=True)
    playlist = ForeignKeyField(Playlist, backref="files", null=True)
    video = ForeignKeyField(Video, backref="files", null=True)

    @classmethod
    def add_new_file(cls, source, target, move_file=True, **kwargs):
        over_ride = kwargs["override"] if "override" in kwargs else None
        file_type = get_file_type(source, override=over_ride)
        extension = "".join(Path(source).suffixes)
        fname = target.stem
        if fname.endswith(".info"):
            fname = fname.replace(".info", "")
        elif fname.endswith(".en"):
            fname = fname.replace(".en", "")

        logger.debug(f"Final Name = {fname}")
        # if file_type == "poster" and cls.poster is not None:
        #     cls.delete_poster()

        f = cls.create(
            path=target.parent,
            filename=fname,
            file_type=file_type,
            extension=extension,
        )

        if "series" in kwargs:
            f.series = kwargs["series"]

        if "channel" in kwargs:
            f.channel = kwargs["channel"]

        if "playlist" in kwargs:
            f.playlist = kwargs["playlist"]

        if "video" in kwargs:
            f.video_id = kwargs["video"].id

        if "youtube_id" in kwargs:
            f.video_id = (
                Video.select().where(Video.youtube_id == kwargs["youtube_id"]).get().id
            )

        f.save()

        if not target.exists():
            logger.debug(f"Creating new file {target} 💥💥💥💥💥")
            my_move_file(source, target)

        else:
            logger.error(f"File {target} already exists")

    def file_string(self):
        pass
        # if self.path is None:
        #     logger.error("Self.path was none.. 💥💥💥💥")
        #     return None
        # if self.filename is None:
        #     self.filename = "asdf"
        # if self.extension is None:
        #     self.extension = "fdsa"

        # p = Path(self.path) / (self.filename + self.extension)
        # return str(p)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Album(BaseModel):
    title = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)
    video = ForeignKeyField(Video, backref="album", null=True)

    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            "release_date": (
                self.release_date.isoformat() if self.release_date else None
            ),
            "video_id": self.video.id if self.video else None,
        }
        return new_dict


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Track(BaseModel):
    title = CharField(null=True)
    track_number = CharField(null=True)
    album = ForeignKeyField(Album, backref="tracks", null=True)
    video = ForeignKeyField(Video, backref="tracks", null=True)

    # this shouldn't be a property of the track. it should be the property of the section
    # that thte track is created for.
    start_time = IntegerField(null=True)
    end_time = IntegerField(null=True)
    length = IntegerField(null=True)

    words = CharField(null=True)
    notes = CharField(null=True)

    def model_to_dict(self):
        new_dict = {
            "id": self.id,
            "title": self.title,
            "track_number": self.track_number,
            "album_id": self.album.id if self.album else None,
            "album_title": self.album.title if self.album else None,
            "video_id": self.video.id if self.video else None,
            "video_title": self.video.title if self.video else None,
        }
        return new_dict


@total_ordering
class Breakpoint(BaseModel):
    # i believe this should all be deleted
    video = ForeignKeyField(Video, backref="breakpoints")
    timestamp = IntegerField()
    # logger.error("DELETE ME (6/9/24) 🐹🐹🐹🐹🐹🐹🐹")

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    class Meta:
        indexes = ((("video", "timestamp"), True),)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Artist(BaseModel):
    name = CharField()
    url = CharField(null=True)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Beat(BaseModel):
    name = CharField()


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class TrackBeat(BaseModel):
    beat = ForeignKeyField(Beat, backref="tracks")
    track = ForeignKeyField(Track, backref="beats")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and track
            (("beat", "track"), True),
        )


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class BeatArtist(BaseModel):
    beat = ForeignKeyField(Beat, backref="artists")
    artist = ForeignKeyField(Artist, backref="beats")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("beat", "artist"), True),
        )


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class PlaylistAlbum(BaseModel):
    album = ForeignKeyField(Album, backref="playlists")
    playlist = ForeignKeyField(Playlist, backref="albums")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("album", "playlist"), True),
        )
