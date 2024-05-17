import json
import os
import re
from datetime import datetime
from pathlib import Path
from functools import total_ordering

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
from hmtc.utils.general import clean_filename, my_copy_file, my_move_file
from hmtc.utils.image import convert_webp_to_png
from hmtc.utils.youtube_functions import (
    download_media_files,
    download_video_info_from_id,
    fetch_ids_from,
)

db_null = PostgresqlDatabase(None)

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH"))


class old_SectionManager:
    def __init__(self, video):
        self.breakpoints = set([])
        self.video = video
        self.duration = video.duration

        for sect in video.sections:
            self.breakpoints.add(sect.start)
            self.breakpoints.add(sect.end)

    @classmethod
    def initialize(cls, video):
        return

    def create_initial_section(self):
        Section.create(
            start=0, end=self.duration, section_type="INITIAL", video=self.video
        )
        self.breakpoints = {0, self.duration}

    def add_breakpoint(self, timestamp):
        if timestamp in self.breakpoints:
            # logger.debug("Section Break already exists. Nothing to do")
            return
        old_section = self.find_section(timestamp=timestamp)
        Section.create(
            start=timestamp,
            end=old_section.end,
            section_type=old_section.section_type,
            video=self.video,
        )
        old_section.end = timestamp
        old_section.save()
        self.breakpoints.add(timestamp)

    def find_section(self, timestamp):
        for sect in self.all_sections:
            if (timestamp + 1) > sect.start and (timestamp - 1) < sect.end:
                return sect
        return None

    def find_both_sections(self, timestamp):
        for sect in self.all_sections:
            if sect.start == timestamp:
                after = sect
            if sect.end == timestamp:
                before = sect

        return before, after

    def delete_breakpoint(self, timestamp):
        if len(self.breakpoints) == 2:
            logger.error("No breakpoints to delete")
            return

        if timestamp not in self.breakpoints:
            logger.debug(f"Breakpoints: {self.breakpoints}")
            logger.error("Breakpoint doesn't exist")
            return

        before, after = self.find_both_sections(timestamp=timestamp)

        if before is None or after is None:
            logger.error("Couldn't find both sections")
            return

        before.end = after.end
        before.save()
        after.delete_instance()

    @property
    def all_sections(self):
        return sorted(self.video.sections, key=lambda x: x.start)

    @property
    def num_sections(self):
        return len(self.all_sections)

    @property
    def oldbreakpoints(self):
        breaks = set([])
        for sect in self.sections:
            breaks.add(sect.start)
            breaks.add(sect.end)
        return breaks


def get_file_type(file: str):

    f = Path(file)
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
        logger.debug(f"Unknown file type: extension is {ext}")
    return filetype


def process_downloaded_files(video, files):
    for downloaded_file in files:

        if downloaded_file.suffix == ".webp":
            converted = convert_webp_to_png(downloaded_file)
            Path(downloaded_file).unlink()
            files.pop(files.index(downloaded_file))
            files.append(converted)
            downloaded_file = converted

        existing = (
            File.select().where(File.filename == downloaded_file.name).get_or_none()
        )
        if not existing:
            if "webp" in downloaded_file.name:
                raise ValueError("asdfWebp files should be converted to png")
            video.add_file(downloaded_file)
            video.save()


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


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Album(BaseModel):
    MEDIA_PATH = STORAGE / "albums"

    name = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Channel(BaseModel):
    MEDIA_PATH = STORAGE / "channels"

    name = CharField(unique=True)
    url = CharField(unique=True)
    youtube_id = CharField(unique=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)

    def check_for_new_videos(self):
        ids = fetch_ids_from(self.url)
        for youtube_id in ids:
            vid, created = Video.get_or_create(youtube_id=youtube_id, channel=self)
            if not created:
                vid.channel = self
                vid.save()
        # once finished updating the playlist, update the last_updated field
        self.last_update_completed = datetime.now()
        self.save()
        logger.debug(f"Finished updating channel {self.name}")

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


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Playlist(BaseModel):
    MEDIA_PATH = STORAGE / "playlists"

    title = CharField(default="Untitled")
    url = CharField(unique=True, null=True)
    youtube_id = CharField(unique=True, null=True)
    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)
    album_per_episode = BooleanField(default=True)
    series = ForeignKeyField(Series, backref="playlists", null=True)
    channel = ForeignKeyField(Channel, backref="playlists", null=True)
    enable_video_downloads = BooleanField(default=True)
    contains_unique_content = BooleanField(default=False)
    # if it doesn't contain unique content, it should probably
    # point to the original
    # eg Omegle Bars Clip 91.4 should point to the original Omegle Bars Clip 91
    # Omegle Bars Clip media would not be downloaded

    def load_info(self):
        logger.error("Deprecated: Playlist.load_info")
        return
        playlist_files = (MEDIA_INFO / "playlists").glob(f"*{self.youtube_id}*")
        for f in playlist_files:
            file_type = get_file_type(f)
            if file_type == "info":
                with open(f, "r") as info_file:
                    info = json.load(info_file)
                    if info["id"] != self.youtube_id:
                        logger.error(
                            f"Info file {f} doesn't match playlist {self.title}"
                        )
                        raise ValueError("Info file doesn't match playlist")
                    ch = Channel.get_or_none(Channel.youtube_id == info["channel_id"])
                    if ch:
                        self.channel = ch

                    self.title = info["title"]
                    self.url = info["webpage_url"]
                    self.save()
            elif file_type == "poster":
                logger.debug("Found the image file")

    @classmethod
    def create_from_yt_id(cls, youtube_id=None, channel=None):

        if youtube_id is None or youtube_id == "":
            logger.error("No youtube ID")
            return None

        info, files = cls.download_video_info(youtube_id)
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

    def load_from_info_file(self):
        logger.error("I think this function is disabled too")
        return
        if self.info is None:
            logger.error(f"No info file found for channel {self.name}")
            return
        fn = Path(self.info.path) / self.info.filename
        with open(fn, "r") as info_file:
            info = json.load(info_file)
            self.title = info["title"]
            self.url = info["webpage_url"]
            self.youtube_id = info["id"]
            self.save()

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

    def __repr__(self):
        return f"Playlist({self.title})"


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Video(BaseModel):
    MEDIA_PATH = STORAGE / "videos"
    sm = None  # section manager

    youtube_id = CharField(unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = TextField(null=True)
    enabled = BooleanField(default=True)
    private = BooleanField(default=False)
    contains_unique_content = BooleanField(default=False)
    channel = ForeignKeyField(Channel, backref="videos", null=True)
    series = ForeignKeyField(Series, backref="videos", null=True)
    playlist = ForeignKeyField(Playlist, backref="videos", null=True)

    def save(self, *args, **kwargs):
        result = super(Video, self).save(*args, **kwargs)
        # if self.num_sections == 0 and self.duration is not None:
        #     Section.create_initial_section(video=self)
        if self.duration is not None:
            Breakpoint.create(video=self, timestamp=0)
            Breakpoint.create(video=self, timestamp=self.duration)
        return result

    @classmethod
    def create_from_yt_id(
        cls, youtube_id=None, channel=None, series=None, playlist=None, enabled=False
    ):
        if youtube_id is None or youtube_id == "":
            logger.error("No youtube ID")
            return None

        existing = cls.get_or_none(cls.youtube_id == youtube_id)
        if existing:
            if playlist is not None:
                logger.error(f"Replacing playlist {existing.playlist} with {playlist}")
                existing.playlist = playlist
                existing.save()

            return None

        info, files = cls.download_video_info(youtube_id)
        if info is None:
            logger.error(f"Error downloading video info for {youtube_id}")
            return None

        vid = cls.create(
            **info, series=series, channel=channel, enabled=enabled, playlist=playlist
        )

        process_downloaded_files(vid, files)

        vid.update_from_yt()

        vid.save()

        return vid

    @property
    def breakpoint_list(self):
        return sorted([x.timestamp for x in self.breakpoints])

    def add_breakpoint(self, timestamp):
        if timestamp in self.breakpoint_list:
            logger.debug("Section Break already exists. Nothing to do")
            return
        if timestamp > self.duration:
            logger.error("Breakpoint can't be greater than duration")
            return
        Breakpoint.create(video=self, timestamp=timestamp)
        logger.debug(f"Adding breakpoint to video {self.title}")

    def delete_breakpoint(self, timestamp):
        if timestamp == 0 or timestamp == self.duration:
            logger.error("Can't delete start or end breakpoints")
            return

        if timestamp not in self.breakpoint_list:
            logger.debug(f"Breakpoints: {self.breakpoint_list}")
            logger.error("Breakpoint doesn't exist")
            return

        bp = Breakpoint.get_or_none(
            (Breakpoint.video == self) & (Breakpoint.timestamp == timestamp)
        )
        if bp is None:
            logger.error("Couldn't find breakpoint")
            return
        bp.my_delete_instance()
        self.breakpoints = Breakpoint.select().where(Breakpoint.video == self)

    @classmethod
    def download_video_info(
        cls, youtube_id=None, thumbnail=True, subtitle=True, info=True
    ):

        download_path = WORKING / "downloads"

        video_info, files = download_video_info_from_id(
            youtube_id, download_path, thumbnail=thumbnail, subtitle=subtitle, info=info
        )

        if video_info["error"] or files is None:
            logger.error(f"{video_info['error_info']}")
            return None, None

        return video_info, files

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.file_stem) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, video=self
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
            .where(File.video == self)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if i:
            return i
        return None

    def download_missing_files(self):

        download_path = WORKING / "downloads"
        media_path = STORAGE / "videos"

        thumbnail = self.poster is None
        subtitle = True
        info = True

        if not (thumbnail or subtitle or info):
            # logger.debug("All files already downloaded")
            return "", []

        video_info, files = download_video_info_from_id(
            self.youtube_id,
            download_path,
            thumbnail=thumbnail,
            subtitle=subtitle,
            info=info,
        )
        if video_info["error"] or files is None:
            logger.error(f"{video_info['error_info']}")
            return None, None
        else:
            new_path = Path(Path(media_path) / video_info["upload_date"][0:4])
            if not new_path.exists():
                new_path.mkdir(parents=True, exist_ok=True)

            # video_info["file_path"] = new_path
            return video_info, files

    def update_episode_number(self, title, templates):
        for template in templates:
            match = re.search(template.template, title)
            if match:
                return match.group(1)

            return ""

    def update_from_yt(self):

        info, files = self.download_missing_files()
        if info and files:
            process_downloaded_files(self, files)

            self.title = info["title"]
            self.upload_date = info["upload_date"]
            self.duration = info["duration"]
            self.description = info["description"]

            self.save()
        # else:
        #     logger.debug(f"No need to update video {self.title}")

    def download_video(self):

        download_path = WORKING / "downloads"
        if self.has_video:
            logger.debug(
                "Video already downloaded. Delete it from the folder to redownload"
            )
            return
        result, files = download_media_files(self.youtube_id, download_path)
        if result:
            for file in files:
                self.add_file(file)

    def extract_audio(self):
        if not self.has_video:
            logger.error(f"No video file found for {self.title}")
            return
        logger.error("Need to redo query before this function will work again.")
        return
        # video_file = (
        #     VideoFile.select(File)
        #     .join(File)
        #     .where((VideoFile.video_id == self.id) & (VideoFile.file_type == "video"))
        # ).get()
        path = Path(video_file.file.path)
        vf = path / video_file.file.filename
        af = path / f"{self.upload_date_str}___{self.youtube_id}.mp3"

        command = f"ffmpeg -i {vf} -vn -acodec libmp3lame -y {af}"
        logger.debug(f"Running command: {command}")
        os.system(command)

        self.add_file(af, file_type="audio")

    def __repr__(self):
        return f"Video({self.title=})"

    @property
    def num_files(self):
        return len(self.existing_files)

    def has_(self, file_type=""):
        if file_type == "":
            raise ValueError("file_type cannot be empty")
        return self.files.where(File.file_type == file_type).count() > 0

    @property
    def file_path(self):
        return STORAGE / "videos"

    @property
    def has_video(self):
        return self.has_("video")

    @property
    def has_audio(self):
        return self.files.where(File.file_type == "audio").count() > 0

    @property
    def has_subtitle(self):
        return self.files.where(File.file_type == "subtitle").count() > 0

    @property
    def has_info(self):
        return self.files.where(File.file_type == "info").count() > 0

    @property
    def upload_date_str(self):
        return self.upload_date.strftime("%Y%m%d")

    @property
    def file_stem(self):
        return f"{self.youtube_id}".lower()

    @property
    def all_sections(self):
        return sorted(self.sections, key=lambda x: x.start)

    @property
    def num_sections(self):
        return len(self.all_sections)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class EpisodeNumberTemplate(BaseModel):
    playlist = ForeignKeyField(Playlist, backref="episode_number_templates")
    template = CharField()


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
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
        return cls.create(
            start=item.start,
            end=item.end,
            section_type=item.section_type,
            video=item.video,
            ordinal=item.ordinal,
        )

    def is_timestamp_in_this_section(self, timestamp):
        return timestamp > self.start and timestamp < self.end

    def __repr__(self):
        return (
            f"Section({self.ordinal} - {self.start}:{self.end} - {self.section_type})"
        )

    def __str__(self):
        return f"Section(id={self.ordinal}, start={self.start}, end={self.end},type={self.section_type})"

    def find_both_sections(self, timestamp):
        before, after = None, None
        for sect in self.all_sections:
            if sect.start == timestamp:
                after = sect
            if sect.end == timestamp:
                before = sect

        return before, after

    @property
    def all_sections(self):
        return sorted(self.video.sections, key=lambda x: x.start)

    @property
    def num_sections(self):
        return len(self.all_sections)

    @property
    def oldbreakpoints(self):
        breaks = set([])
        for sect in self.sections:
            breaks.add(sect.start)
            breaks.add(sect.end)
        return breaks


@total_ordering
class Breakpoint(BaseModel):
    video = ForeignKeyField(Video, backref="breakpoints")
    timestamp = IntegerField()

    def __lt__(self, other):
        return self.timestamp < other.timestamp


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

        file_type = get_file_type(source)
        extension = "".join(Path(source).suffixes)
        fname = target.stem
        if fname.endswith(".info"):
            fname = fname.replace(".info", "")
        elif fname.endswith(".en"):
            fname = fname.replace(".en", "")

        logger.debug(f"Final Name = {fname}")
        # if file_type == "poster" and cls.poster is not None:
        #     cls.delete_poster()

        f, created = cls.get_or_create(
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
            f.video = kwargs["video"]

        f.save()

        if created:
            if move_file:
                my_move_file(source, target)
            else:
                my_copy_file(source, target)
            logger.debug(f"Created new file: {f.filename}")

    @classmethod
    def get_file_model(cls):
        logger.debug(f"Getting file model for {cls.__name__}")
        return cls.__name__

    def delete_poster(self):
        poster = self.poster
        if poster:
            poster.delete_instance()
            logger.debug(f"Deleted poster for channel {self.name}")
            logger.debug(f"Path({poster.filename}).unlink()")

    def delete_info(self):
        info = self.info
        if info:
            info.delete_instance()
            logger.debug(f"Deleted info for channel {self.name}")
            logger.debug(f"Path({info.filename}).unlink()")

    @property
    def file_string(self):
        p = Path(self.path) / (self.filename + self.extension)
        return str(p)
