from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import peewee
from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import File, Playlist, Series, Video
from hmtc.mods.file import FileManager
from hmtc.schemas.base import BaseItem
from hmtc.utils.general import my_move_file, read_json_file
from hmtc.utils.image import convert_webp_to_png
from hmtc.utils.opencv.second import extract_frames
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"])


@dataclass(frozen=True, kw_only=True)
class VideoItem(BaseItem):
    db_model = Video
    title: str = None
    youtube_id: str = None
    url: str = None
    last_update_completed = None
    episode: str = None
    upload_date: datetime = None
    duration: int = 0
    description: str = None
    contains_unique_content: bool = False
    has_chapters: bool = False
    manually_edited: bool = False
    series_name: str = "Default"
    playlist_name: str = "Default"
    channel_id: int = None
    playlist_id: int = None
    series_id: int = None

    # has_video_file: bool = False
    # has_audio_file: bool = False
    # has_subtitle_file: bool = False
    # has_poster_file: bool = False
    # has_info_file: bool = False

    @staticmethod
    def has_audio_file(id):
        return len(VideoItem.get_audio_file_path(id)) > 0

    @staticmethod
    def get_audio_file_path(id):
        audio_file = (
            File.select()
            .where((File.video_id == id) & (File.file_type == "audio"))
            .get()
        )
        if audio_file is None:
            return None
        return f"{audio_file.path}/{audio_file.filename}"

    @staticmethod
    def has_poster_file(id):
        poster = VideoItem.get_poster_file_path(id)
        logger.debug(f"Poster: {poster}")
        return poster is None

    @staticmethod
    def get_poster_file_path(id):
        poster_file = (
            File.select()
            .where((File.video_id == id) & (File.file_type == "poster"))
            .get()
        )
        if poster_file is None:
            return None
        return f"{poster_file.path}/{poster_file.filename}"

    @staticmethod
    def has_frame_files(id):
        return len(VideoItem.get_frame_file_path(id)) > 0

    @staticmethod
    def get_frame_file_path(id):
        files = File.select().where((File.video_id == id) & (File.file_type == "frame"))
        # logger.debug(f"Files found: {len(files)}")
        return files

    @staticmethod
    def has_video_file(id):
        return len(VideoItem.get_video_file_path(id)) > 0

    @staticmethod
    def get_video_file_path(id):
        files = File.select().where((File.video_id == id) & (File.file_type == "video"))
        # logger.debug(f"Files found: {len(files)}")
        return files

    @classmethod
    def count_videos(cls, enabled: bool = True):
        return cls.db_model.select().where(cls.enabled == enabled).count()

    @classmethod
    def count_no_duration(cls):
        return cls.db_model.select().where(cls.db_model.duration.is_null()).count()

    @staticmethod
    def count_unique():
        return Video.select().where(Video.contains_unique_content == True).count()

    @classmethod
    def grab_page_from_db(
        cls,
        current_page,
        per_page,
        text_search=None,
        sort_column=None,
        sort_order=None,
        series_filter=None,
        playlist_filter=None,
        include_no_durations=False,
        include_unique_content=True,
        include_nonunique_content=False,
        include_manually_edited=False,
    ):

        # sort column is the column 'string' to sort by
        query = Video.select()
        # and = all
        # 1 and 0 = unique
        # 0 and 1 = nonunique
        # 0 and 0 = error
        if include_unique_content and include_nonunique_content:
            query = query
        elif include_unique_content:
            query = query.where(Video.contains_unique_content == True)

        elif include_nonunique_content:
            query = query.where(Video.contains_unique_content == False)
        else:
            logger.error("Tried disabling unique filter but you can't 😃😃😃😃😃")
            query = query

        if not include_no_durations:
            query = query.where(Video.duration > 0)

        if series_filter:
            if series_filter["title"] == "All Series":
                query = query
            else:
                query = query.join(Series).where(Series.name == series_filter["title"])

        if playlist_filter:
            if playlist_filter["title"] == "No Playlists":
                query = query.where(cls.db_model.playlist.is_null())
            else:
                query = query.join(Playlist).where(
                    Playlist.title == playlist_filter["title"]
                )
        if text_search:
            query = query.where(
                (cls.db_model.title.contains(text_search))
                | (cls.db_model.url.contains(text_search))
                | (cls.db_model.youtube_id.contains(text_search))
            )

        sort_field = None

        if sort_column is not None:
            sort_field = cls.get_sort_field(sort_column, sort_order)

        if sort_field is not None:
            items = query.order_by(sort_field)
        else:
            items = query.order_by(cls.id.asc())

        if not items:
            return [], []

        query = items.paginate(current_page, per_page)

        page_of_items = [
            cls(
                title=item.title,
                url=item.url,
                id=item.id,
                youtube_id=item.youtube_id,
                enabled=item.enabled,
                manually_edited=True,
                upload_date=item.upload_date,
                duration=item.duration,
                description=item.description,
                contains_unique_content=item.contains_unique_content,
                has_chapters=item.has_chapters,
                series_name=(item.series.name if item.series != "NOSERIES" else "---"),
                playlist_name=(item.playlist.title if item.playlist else "---"),
            )
            for item in query
        ]
        return page_of_items, items

    def db_object(self):
        return self.db_model.get_or_none(self.db_model.id == self.id)

    @classmethod
    def from_orm(cls, db_object):
        return cls(
            title=db_object.title,
            url=db_object.url,
            id=db_object.id,
            youtube_id=db_object.youtube_id,
            enabled=db_object.enabled,
            manually_edited=True,
            upload_date=db_object.upload_date,
            duration=db_object.duration,
            description=db_object.description,
            contains_unique_content=db_object.contains_unique_content,
            has_chapters=db_object.has_chapters,
        )

    def add_file(self, file, file_type=None):
        logger.debug(f"In VideoItem.add_file: {file}")

        extension = "".join(Path(file).suffixes)
        clean_name = Path(file).stem
        final_name = STORAGE / "videos" / self.youtube_id / (clean_name + extension)
        final_name2 = str(final_name.name).replace(".info.info", ".info")
        if ".info" in str(file):
            data = read_json_file(file)
            vid = Video.get(Video.id == self.id)
            vid.title = data["title"]
            vid.url = data["webpage_url"]
            vid.upload_date = data["upload_date"]
            vid.duration = int(data["duration"])
            vid.description = data["description"]
            vid.save()

        File.create(
            path=final_name.parent,
            filename=final_name2,
            move_file=True,
            video_id=self.id,
            file_type=file_type,
        )
        my_move_file(file, final_name)

    def extract_frames(self):
        return extract_frames(self.get_video_file_path(self.id), self.youtube_id)

    def add_frame(self, file):
        Video.add_file(self.youtube_id, file, move_file=False, override="frame")
        self.save_to_db()

    def update_from_youtube(self):
        # download files to temp folder
        info, files = get_video_info(youtube_id=self.youtube_id, output_folder=WORKING)

        # logger.debug(f"Info: {info}")
        # logger.debug(f"Files: {files}")
        vid = Video.select().where(Video.id == self.id).get()
        for file in files:
            logger.debug(f"Processing files in VideoItem.update_from_youtube: {file}")
            FileManager.add_path_to_video(file, vid)

        vid.title = info["title"]
        vid.url = info["webpage_url"]
        vid.youtube_id = info["id"]
        vid.upload_date = info["upload_date"]
        vid.enabled = True
        vid.duration = info["duration"]
        vid.description = info["description"]
        vid.save()
        logger.success(f"Grabbed metadata for {vid.title} from youtube")

    def update_series(self, series_name):
        series = Series.select().where(Series.name == series_name).get()
        vid = Video.select().where(Video.id == self.id).get()
        vid.series = series
        vid.save()

    def update_database_object(self):
        vid = Video.select().where(Video.id == self.id).get()
        vid.title = self.title
        vid.url = self.url
        vid.youtube_id = self.youtube_id
        vid.enabled = self.enabled
        vid.duration = self.duration
        vid.description = self.description
        vid.contains_unique_content = self.contains_unique_content
        vid.has_chapters = self.has_chapters
        vid.save()

    def process_downloaded_files(self, files):
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
                self.add_file(downloaded_file)
                self.save()

    @staticmethod
    def get_downloaded_stats_by_series():
        query = (
            Video.select(
                fn.SUM(Video.duration).alias("downloaded"),
                Series.name,
            )
            .join(Series, peewee.JOIN.RIGHT_OUTER)
            .where(
                Video.id.in_(
                    File.select(File.video_id).where(File.file_type == "video")
                )
            )
            .group_by(Series.name)
        )

        query2 = (
            Video.select(
                fn.SUM(Video.duration).alias("total"),
                Series.name,
            )
            .join(Series)
            .group_by(Series.name)
        )
        downloaded = [(a.series, a.downloaded) for a in query]
        total = [(b.series, b.total) for b in query2]
        combined = []
        for t in total:
            if t[0].name not in [d[0].name for d in downloaded]:
                combined.append(({"name": t[0].name, "downloaded": 0, "total": t[1]}))
        for d in downloaded:
            for t in total:
                if d[0].name == t[0].name:
                    combined.append(
                        {"name": d[0].name, "downloaded": d[1], "total": t[1]}
                    )
                    break
        return sorted(combined, key=lambda series: series["name"], reverse=True)

    def download_video(self):
        def my_hook(*args):
            pass

        logger.info(f"Downloading video: {self.title}")
        info, files = download_video_file(
            self.youtube_id, WORKING, progress_hook=my_hook
        )

        vid = Video.select().where(Video.id == self.id).get()
        for file in files:

            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)

    @staticmethod
    def get_vids_with_no_media_files(limit=10):
        vids = (
            Video.select()
            .where(
                (Video.contains_unique_content == True)
                & (
                    Video.id.not_in(
                        File.select(File.video_id).where(File.file_type == "video")
                    )
                )
            )
            .order_by(Video.duration.asc())
            .limit(limit)
        )

        vid_items = [VideoItem.from_orm(v) for v in vids]
        return vid_items

    @staticmethod
    def count_vids_with_media_files():
        return (
            Video.select()
            .where(
                (Video.contains_unique_content == True)
                & (
                    Video.id.in_(
                        File.select(File.video_id).where(File.file_type == "video")
                    )
                )
            )
            .count()
        )
