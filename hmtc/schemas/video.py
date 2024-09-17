from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import peewee
from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import Album as AlbumTable
from hmtc.models import File, Playlist, Series, Video, Channel, YoutubeSeries
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
    channel_id: int = None
    playlist_id: int = None
    series_id: int = None
    youtube_series_id: int = None
    youtube_series_title: str = None
    series: Series = None
    channel: Channel = None
    playlist: Playlist = None
    youtube_series: YoutubeSeries = None
    jellyfin_id: str = None

    # has_video_file: bool = False
    # has_audio_file: bool = False
    # has_subtitle_file: bool = False
    # has_poster_file: bool = False
    # has_info_file: bool = False

    ### 🟣🟣🟣 Static Methods
    @staticmethod
    def has_audio_file(id):
        return len(VideoItem.get_audio_file_path(id)) > 0

    @staticmethod
    def get_audio_file_path(id):
        audio_file = (
            File.select()
            .where((File.video_id == id) & (File.file_type == "audio"))
            .get_or_none()
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
        return Video.select().where(cls.enabled == enabled).count()

    @classmethod
    def count_no_duration(cls):
        return Video.select().where(Video.duration.is_null()).count()

    @staticmethod
    def count_unique():
        return Video.select().where(Video.contains_unique_content == True).count()

    @staticmethod
    def get_downloaded_stats_by_series():
        query = (
            Video.select(
                fn.SUM(Video.duration).alias("downloaded"),
                Series.name,
            )
            .join(Series, peewee.JOIN.RIGHT_OUTER)
            .where(
                (
                    Video.id.in_(
                        File.select(File.video_id).where(File.file_type == "video")
                    )
                )
                & (Video.contains_unique_content == True)
            )
            .group_by(Series.name)
        )

        query2 = (
            Video.select(
                fn.SUM(Video.duration).alias("total"),
                Series.name,
            )
            .join(Series)
            .where(Video.contains_unique_content == True)
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

    @staticmethod
    def get_album(video_id):
        vid = Video.select().join(AlbumTable).where(Video.id == video_id).get_or_none()
        if vid:
            return vid.album.get_or_none()
        return None

    @staticmethod
    def get_by_youtube_id(youtube_id):
        return Video.select().where(Video.youtube_id == youtube_id).get_or_none()

    @staticmethod
    def get_unique_with_no_durations():
        return Video.select().where(
            (Video.duration.is_null() & Video.contains_unique_content == True)
        )

    @staticmethod
    def get_by_id(video_id):
        return Video.select().where(Video.id == video_id).get_or_none()

    @staticmethod
    def get_youtube_ids():

        return Video.select(Video.youtube_id)

    @staticmethod
    def create_from_youtube_id(youtube_id):
        logger.debug(f"Creating video from youtube id: {youtube_id}")
        info, files = get_video_info(youtube_id=youtube_id, output_folder=WORKING)
        try:
            series = Series.get(Series.name.contains("UNSORTED"))
        except:
            logger.error("Series Doesn't Exist!")
            return
        try:
            channel = Channel.get(Channel.youtube_id == info["channel_id"])
        except:
            logger.error("Channel Doesn't Exist!")
            return

        # he posts 'shorts' on his main channel that arent unique
        if channel.name == "Harry Mack" and info["duration"] > 120:
            unique = True
        else:
            unique = False

        vid = Video.create(
            title=info["title"],
            url=info["webpage_url"],
            youtube_id=info["id"],
            upload_date=info["upload_date"],
            enabled=True,
            duration=info["duration"],
            description=info["description"],
            series_id=series.id,
            channel_id=channel.id,
            contains_unique_content=unique,
        )
        logger.debug(f"Created video: {vid.title}")

        for file in files:
            logger.debug(
                f"Processing files in VideoItem.create_from_youtube_id: {file}"
            )
            FileManager.add_path_to_video(file, vid)
        return vid

    @staticmethod
    def grab_info_from_youtube(youtube_id):
        info, files = get_video_info(youtube_id=youtube_id, output_folder=WORKING)
        return info

    @staticmethod
    def get_vids_with_no_channel():
        return Video.select().where(Video.channel.is_null())

    @staticmethod
    def get_vids_with_no_album():
        all_vids = Video.select().where(Video.contains_unique_content == True)
        vids_with_albums = (
            Video.select().join(AlbumTable).where(Video.contains_unique_content == True)
        )
        vids_missing_albums = all_vids - vids_with_albums
        return vids_missing_albums

    @staticmethod
    def get_vids_with_no_episode_number():
        vids = Video.select().where(
            (
                Video.title.is_null(False)
                & Video.episode.is_null()
                & Video.contains_unique_content
                == True
            )
        )
        return [VideoItem.from_orm(v) for v in vids]

    @staticmethod
    def get_base_video_ids():
        vid_ids = (
            Video.select(Video.id)
            .where(
                (Video.title.is_null(False))
                & (Video.contains_unique_content == True)
                & (Video.duration.is_null(False))
            )
            .order_by(Video.upload_date.desc())
        )
        return [v.id for v in vid_ids]

    @staticmethod
    def get_filtered_video_ids(
        text_search=None,
        sort_by=None,
        sort_order=None,
        series_filter=None,
        youtube_series_filter=None,
        include_no_durations=False,
        include_unique_content=True,
        include_nonunique_content=False,
    ):
        query = VideoItem.create_filtered_video_ids_query(
            text_search=text_search,
            sort_by=sort_by,
            sort_order=sort_order,
            series_filter=series_filter,
            include_no_durations=include_no_durations,
            include_unique_content=include_unique_content,
            include_nonunique_content=include_nonunique_content,
            youtube_series_filter=youtube_series_filter,
        )

        if query == ([], []):
            return [], []

        return [v.id for v in query]

    @staticmethod
    def create_filtered_video_ids_query(
        text_search=None,
        sort_by=None,
        sort_order=None,
        series_filter=None,
        youtube_series_filter=None,
        include_no_durations=False,
        include_unique_content=True,
        include_nonunique_content=False,
    ):
        query = Video.select(Video.id).where((Video.title.is_null(False)))

        # and = all
        # 1 and 0 = unique
        # 0 and 1 = nonunique
        # 0 and 0 = error
        if include_unique_content and include_nonunique_content:
            query = query
        elif include_unique_content:
            query = query.where(Video.contains_unique_content == True)

        elif include_nonunique_content:
            query = query.where(Video.contains_unique_content is False)
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

        if youtube_series_filter:
            if youtube_series_filter["title"] == "No youtube_series":
                query = query.where(Video.youtube_series.is_null())
            else:
                query = query.join(YoutubeSeries).where(
                    YoutubeSeries.title == youtube_series_filter["title"]
                )

        if text_search:
            query = query.where(
                (Video.title.contains(text_search))
                | (Video.url.contains(text_search))
                | (Video.youtube_id.contains(text_search))
            )

        # not really sure how this actually works
        # sort column is the column 'string' to sort by
        sort_field = None

        if sort_by is not None:

            sort_field = VideoItem.get_sort_field(sort_by, sort_order)
            if sort_order == "asc":
                sort_field = sort_field.asc()
            else:
                sort_field = sort_field.desc()
        else:
            sort_field = Video.upload_date.desc()

        q = query.order_by(sort_field)

        if not q:
            # logger.debug(f"No items found for query: {query.sql()}")
            return [], []

        return q

    @staticmethod
    def grab_list_of_video_details(ids):

        vids = [VideoItem.get_details_for_video(id=vid_id) for vid_id in ids]

        return vids

    @staticmethod
    def get_details_for_video(id: int):
        vid = (
            Video.select(
                Video,
                YoutubeSeries.title,
                Channel.name,
            )
            .join(
                YoutubeSeries,
                peewee.JOIN.LEFT_OUTER,
                on=(Video.youtube_series_id == YoutubeSeries.id),
            )
            .switch(Video)
            .join(Channel)
            .where(Video.id == id)
        ).get()

        return VideoItem.from_orm(vid)

    ### 🟣🟣🟣 Instance Methods
    def set_episode_number(self, episode_number: int):
        vid = Video.get(Video.id == self.id)
        vid.episode = episode_number
        vid.save()

    def db_object(self):
        return self.db_model.get_or_none(self.db_model.id == self.id)

    def add_file(self, file, file_type=None):
        logger.debug(f"In VideoItem.add_file: {file}")
        logger.debug("Fix this 🤡🤡🤡🤡🤡🤡🤡")
        exit()
        extension = "".join(Path(file).suffixes)
        clean_name = Path(file).stem
        final_name = STORAGE / "videos" / self.youtube_id / (clean_name + extension)
        # LOL
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
        vid.episode = self.episode
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

    def db_object(self):
        logger.debug("🚨🚨🚨🚨 I want to deprecate this 8-21-24 🚨🚨🚨🚨")
        return self.db_model.get_or_none(self.db_model.id == self.id)

    @classmethod
    def grab_page_from_db(
        cls,
        current_page,
        per_page,
        text_search=None,
        sort_by=None,
        sort_order=None,
        series_filter=None,
        playlist_filter=None,
        # channel_filter=None,
        include_no_durations=False,
        include_unique_content=True,
        include_nonunique_content=False,
        include_manually_edited=False,
        youtube_series_filter=None,
    ):

        query = VideoItem.create_filtered_video_ids_query(
            text_search=text_search,
            sort_by=sort_by,
            sort_order=sort_order,
            series_filter=series_filter,
            include_no_durations=include_no_durations,
            include_unique_content=include_unique_content,
            include_nonunique_content=include_nonunique_content,
            youtube_series_filter=youtube_series_filter,
        )

        page_of_items = [
            VideoItem.from_orm(item) for item in query.paginate(current_page, per_page)
        ]
        return page_of_items

    @staticmethod
    def from_orm(db_object):
        # logger.debug("Creating VideoItem from ORM DB Object: {db_object}")
        # I'm pretty sure this is the WRONG to do this... 9/16/24
        return VideoItem(
            title=db_object.title,
            url=db_object.url,
            id=db_object.id,
            youtube_id=db_object.youtube_id,
            enabled=db_object.enabled,
            episode=db_object.episode,
            manually_edited=True,
            upload_date=db_object.upload_date,
            duration=db_object.duration,
            description=db_object.description,
            contains_unique_content=db_object.contains_unique_content,
            has_chapters=db_object.has_chapters,
            jellyfin_id=db_object.jellyfin_id,
            # youtube_series_id=db_object.youtube_series_id,
            channel=db_object.channel if db_object.channel else None,
            youtube_series=(
                db_object.youtube_series if db_object.youtube_series else None
            ),
            playlist=db_object.playlist if db_object.playlist else None,
            series=db_object.series if db_object.series else None,
        )

    @staticmethod
    def video_details_query():
        # in progress 9/7/24
        return (
            Video.select(Video, Channel, Series, YoutubeSeries.title, Playlist)
            .join(Channel, peewee.JOIN.LEFT_OUTER)
            .switch(Video)
            .join(Series)
            .switch(Video)
            .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
            .switch(Video)
            .join(Playlist, peewee.JOIN.LEFT_OUTER)
            .where(Video.contains_unique_content == True)
        )

    ### 🟣🟣🟣 Temporary Methods

    # this is a temporary function to update the episode numbers for videos
    # as of 8-16-2024
    def update_episode_number(self):
        omegle = [
            "Omegle Bars ([0-9]+)",
            "Omegle Bars Episode ([0-9]+)",
            "Omegle Bars Ep. ([0-9]+)",
        ]
        ww = [
            r"Wordplay Wednesday \#([0-9]+)",
            r"Wordplay Wednesday Episode ([0-9]+)",
            r"Wordplay Wednesday w/ Harry Mack.*([0-9]+)",
            r"Wordplay Tuesday \#([0-9]+)",
        ]
        guerrilla = [
            "Guerrilla Bars ([0-9]+)",
            r"Guerrilla Bars \(Episode ([0-9]+)",
            "Guerrilla Bars Episode ([0-9]+)",
        ]

        if "omegle" in self.title.lower():
            for o in omegle:
                match = re.search(o, self.title)
                if match:
                    v = Video.get(Video.id == self.id)
                    v.episode = match.group(1)
                    v.save()
                    return

        elif "wordplay" in self.title.lower():
            for w in ww:
                match = re.search(w, self.title)
                if match:
                    v = Video.get(Video.id == self.id)
                    v.episode = match.group(1)
                    v.save()
                    return
        elif "guerrilla" in self.title.lower():
            for g in guerrilla:
                match = re.search(g, self.title)
                if match:
                    v = Video.get(Video.id == self.id)
                    v.episode = match.group(1)
                    v.save()
                    return
        else:
            # logger.debug(f"Could not find episode number for {self.title}")
            return
