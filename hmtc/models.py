import json
import os
import re
from datetime import datetime
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
from hmtc.utils.general import my_move_file, my_copy_file, clean_filename
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

    def delete_instance(self, *args, **kwargs):
        self.deleted_at = datetime.now()
        self.save()
        return None

    @classmethod
    def active(cls):
        return cls.select().where(cls.deleted_at.is_null()).distinct()

    class Meta:
        database = db_null


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Series(BaseModel):
    name = CharField(unique=True)
    start_date = DateField(null=True)
    end_date = DateField(null=True)

    MEDIA_PATH = STORAGE / "series"

    @property
    def enabled_videos(self):
        return self.videos.where(Video.enabled == True).count()

    @property
    def total_videos(self):
        return self.videos.count()

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.name.lower()) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, series=self
        )

    def delete_poster(self):
        poster = self.poster
        if poster:
            poster.delete_instance()
            logger.debug(f"Deleted poster for channel {self.name}")
            logger.debug(f"Path({poster.filename}).unlink()")

    @property
    def poster(self):
        logger.debug(f"Getting poster for series {self.name}")
        p = (
            File.select()
            .where(File.file_type == "poster")
            .where(File.series_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if p:
            return p
        return None


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Album(BaseModel):
    name = CharField(unique=True)
    release_date = DateField(null=True)
    series = ForeignKeyField(Series, backref="albums", null=True)


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Channel(BaseModel):

    from hmtc.config import init_config

    MEDIA_PATH = STORAGE / "channels"
    name = CharField(unique=True)
    url = CharField(unique=True)
    youtube_id = CharField(unique=True)

    enabled = BooleanField(default=True)
    last_update_completed = DateTimeField(null=True)

    def check_for_new_videos(self):
        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"

        # ensure that all videos in the db point to the correct channel
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

    def delete_poster(self):
        poster = self.poster
        if poster:
            poster.delete_instance()
            logger.debug(f"Deleted poster for channel {self.name}")
            logger.debug(f"Path({poster.filename}).unlink()")

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
        logger.debug(f"Getting poster for channel {self.name}")
        p = (
            File.select()
            .where(File.file_type == "poster")
            .where(File.channel_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if p:
            return p
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
    add_videos_enabled = BooleanField(default=True)
    playlist_count = IntegerField(default=0)

    def load_info(self):
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
                    self.playlist_count = int(info["playlist_count"])
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

    def check_for_new_videos(self):

        download_path = WORKING / "downloads"

        # download list of videos from youtube
        # as a list of youtube ids as strings "example abCdgeseg12"
        ids = fetch_ids_from(self.url, download_path)
        logger.debug(f"Found {len(ids)} videos in playlist {self.title}")
        for youtube_id in ids:
            if youtube_id == "":
                logger.error("No youtube ID")
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
        logger.success(f"Finished updating playlist {self.title}")

    def load_from_info_file(self):
        if self.info is None:
            logger.error(f"No info file found for channel {self.name}")
            return
        fn = Path(self.info.path) / self.info.filename
        with open(fn, "r") as info_file:
            info = json.load(info_file)
            self.title = info["title"]
            self.url = info["webpage_url"]
            self.youtube_id = info["id"]
            self.playlist_count = info["playlist_count"]

            self.save()

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.title.lower()) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, playlist=self
        )

    def delete_poster(self):
        poster = self.poster
        if poster:
            poster.delete_instance()
            logger.debug(f"Deleted poster for playlist {self.title}")
            logger.debug(f"Path({poster.filename}).unlink()")

    @property
    def poster(self):
        try:
            s = self.name
        except AttributeError:
            s = self.title
        logger.debug(f"Getting poster for object {s}")
        p = (
            File.select()
            .where(File.file_type == "poster")
            .where(File.playlist_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if p:
            return p
        logger.debug(f"No poster found for {s}")
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
        pass

    def __repr__(self):
        return f"Playlist({self.title=})"


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class Video(BaseModel):
    youtube_id = CharField(unique=True)
    url = CharField(null=True)
    title = CharField(null=True)
    episode = CharField(null=True)
    upload_date = DateField(null=True)
    duration = IntegerField(null=True)
    description = TextField(null=True)

    # file_path = CharField()  # should be a relative path
    enabled = BooleanField(default=True)
    private = BooleanField(default=False)
    #    error = BooleanField(default=False)
    #    error_info = CharField(null=True)
    channel = ForeignKeyField(Channel, backref="videos", null=True)
    series = ForeignKeyField(Series, backref="videos", null=True)
    playlist = ForeignKeyField(Playlist, backref="videos", null=True)

    MEDIA_PATH = STORAGE / "videos"

    @classmethod
    def create_from_yt_id(
        cls, youtube_id=None, channel=None, series=None, playlist=None, enabled=None
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

        vid = cls.create(**info, series=series, channel=channel, enabled=enabled)
        if vid and channel:
            vid.channel = channel
        if enabled is not None:
            vid.enabled = enabled

        process_downloaded_files(vid, files)

        vid.update_from_yt()

        vid.create_initial_section()

        vid.save()

        if playlist:
            PlaylistVideo.create(video=vid, playlist=playlist)

        return vid

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

    def add_file(self, filename, move_file=True):
        extension = "".join(Path(filename).suffixes)
        final_name = Path(self.MEDIA_PATH) / (
            clean_filename(self.file_stem) + extension
        )
        File.add_new_file(
            source=filename, target=final_name, move_file=move_file, video=self
        )

    def delete_poster(self):
        poster = self.poster
        if poster:
            poster.delete_instance()
            logger.debug(f"Deleted poster for playlist {self.title}")
            logger.debug(f"Path({poster.filename}).unlink()")

    @property
    def poster(self):
        try:
            s = self.name
        except AttributeError:
            s = self.title
        logger.debug(f"Getting poster for object {s}")
        p = (
            File.select()
            .where(File.file_type == "poster")
            .where(File.video_id == self.id)
            .get_or_none()
        )
        # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
        if p:
            return p
        logger.debug(f"No poster found for {s}")
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

        download_path = config.get("PATHS", "DOWNLOAD")
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
        logger.error(f"Need to redo query before this function will work again.")
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


def get_section_with_timestamp(video, timestamp):
    for sect in video.sections:
        if sect.is_timestamp_in_this_section(timestamp):
            return sect
    return None


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
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
class PlaylistVideo(BaseModel):
    video = ForeignKeyField(Video, backref="playlists")
    playlist = ForeignKeyField(Playlist, backref="videos")

    class Meta:
        indexes = (
            # Create a unique composite index on beat and Artist
            (("video", "playlist"), True),
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


# def add_files_to_db():

#     # this will add existing media files to the database
#     media_path = Path("/mnt/c/DATA/hmtc_fqweriles/media")
#     for mp in media_path.rglob("*"):
#         if mp.is_file() and mp.stem[4] == "-":
#             # currently date is in YYYY-MM-DD format
#             # need to replace with YYYYMMDD
#             new_name = mp.name.replace("-", "")
#             mp = mp.rename(mp.parent / new_name)

#         existing = File.select().where(
#             (File.filename == mp.name)
#             & (File.local_path == mp.parent)
#             & (File.extension == mp.suffix)
#         )
#         if not existing:
#             f = File.create(
#                 local_path=mp.parent,
#                 filename=mp.name,
#                 extension=mp.suffix,
#             )


# def create_video_file_associations():
#     videos = Video.select()
#     for vid in videos:
#         files = File.select().where(File.filename.contains(vid.youtube_id))
#         for file in files:
#             VideoFile.create(file=file, video=vid, file_type=get_file_type(file))


## 🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬🧬
class File(BaseModel):
    path = CharField(null=True)

    filename = CharField()
    extension = CharField(null=True)
    file_type = CharField(null=True)
    WORKING_PATH = WORKING / "uploads"
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
