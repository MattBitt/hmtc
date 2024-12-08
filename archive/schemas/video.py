import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter

import peewee
from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Channel,
    Series,
    YoutubeSeries,
)
from hmtc.models import Section as SectionModel
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Track as TrackModel
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.schemas.base import BaseItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.section import SectionManager
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.utils.general import my_move_file, read_json_file
from hmtc.utils.image import convert_webp_to_png
from hmtc.utils.jellyfin_functions import refresh_library
from hmtc.utils.xml_creator import create_album_xml
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"])


@dataclass(frozen=True, kw_only=True)
class VideoItem(BaseItem):
    db_model = VideoModel
    item_type: str = "VIDEO"
    id: int = None
    title: str = None
    youtube_id: str = None
    url: str = None
    episode: str = None
    upload_date: datetime = None
    duration: int = 0
    description: str = None
    unique_content: bool = False

    jellyfin_id: str = None

    # relationships
    # Video is one of many
    album_id: int = 0
    album: AlbumModel = None

    channel_id: int = 0

    series_id: int = 0

    youtube_series_id: int = 0

    # Video has multiple
    section_ids: list = field(default_factory=list)
    sections: list = field(default_factory=list)

    files: list = field(default_factory=list)

    superchats: list = field(default_factory=list)
    superchat_count: int = 0
    segments: list = field(default_factory=list)
    segment_count: int = 0

    @staticmethod
    def from_model(video: VideoModel) -> "VideoItem":

        return VideoItem(
            id=video.id,
            title=video.title,
            youtube_id=video.youtube_id,
            url=video.url,
            episode=video.episode,
            upload_date=video.upload_date,
            duration=video.duration,
            description=video.description,
            unique_content=video.unique_content,
            jellyfin_id=video.jellyfin_id,
            album=video.album,
            album_id=video.album_id,
            channel_id=video.channel_id,
            youtube_series_id=video.youtube_series_id,
            series_id=video.series_id,
            sections=[],
            superchats=video.superchats,
        )

    def serialize(self) -> dict:

        return {
            "id": self.id,
            "title": self.title,
            "youtube_id": self.youtube_id,
            "url": self.url,
            "episode": self.episode,
            "upload_date": str(self.upload_date),
            "duration": self.duration,
            "description": self.description,
            "unique_content": self.unique_content,
            "jellyfin_id": self.jellyfin_id,
            "section_info": {
                "section_count": len(self.sections),
                "track_count": 15,
                "my_new_column": 0.156,
            },
            "channel_id": self.channel_id,
            "youtube_series_id": self.youtube_series_id,
            "series_id": self.series_id,
            "album": self.album.title if self.album else None,
            "section_ids": [],
            "sections": [],
            "superchats_count": 456,
            "segments_count": 789,
        }

    @staticmethod
    def update_from_dict(video_id, new_data):
        video = VideoModel.get(VideoModel.id == video_id)
        video.title = new_data.get("title", "")
        video.url = new_data.get("url", "")
        video.youtube_id = new_data.get("youtube_id", "")
        video.enabled = new_data.get("enabled", True)
        video.episode = new_data.get("episode", "")
        video.duration = new_data.get("duration", 0)
        video.description = new_data.get("description", "")
        video.contains_unique_content = new_data.get("contains_unique_content", False)
        video.save()

    @staticmethod
    def delete_id(video_id):
        video = VideoModel.get(VideoModel.id == video_id)
        for file in video.files:
            FileManager.delete_file(file.id)
        for section in video.sections:
            for file in section.track.files:
                FileManager.delete_file(file.id)
            section.track.delete_instance()
            SectionManager.delete_section(section.id)
        video.delete_instance(recursive=True)

    @staticmethod
    def get_downloaded_stats_by_series():
        logger.error("🧪🧪🧪🧪🧪🧪 Is this used????? 🧪🧪🧪🧪🧪🧪 10/26/24")
        query = (
            VideoModel.select(
                fn.SUM(VideoModel.duration).alias("downloaded"),
                Series.name,
            )
            .join(Series, peewee.JOIN.RIGHT_OUTER)
            .where(
                (
                    VideoModel.id.in_(
                        FileItem.select(FileItem.video_id).where(
                            FileItem.file_type == "video"
                        )
                    )
                )
                & (VideoModel.contains_unique_content == True)
            )
            .group_by(Series.name)
        )

        query2 = (
            VideoModel.select(
                fn.SUM(VideoModel.duration).alias("total"),
                Series.name,
            )
            .join(Series)
            .where(VideoModel.contains_unique_content == True)
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
    def create_from_youtube_id(youtube_id):

        logger.debug(f"Creating video from youtube id: {youtube_id}")
        info, files = get_video_info(youtube_id=youtube_id, output_folder=WORKING)
        try:
            series = Series.get(Series.name.contains("UNSORTED"))
        except Exception as e:
            logger.error(f"Series Doesn't Exist! {e}")
            return
        try:
            channel = Channel.get(Channel.youtube_id == info["channel_id"])
        except Exception as e:
            logger.error(f"Channel Doesn't Exist! {e}")
            return

        # he posts 'shorts' on his main channel that arent unique
        if "Clips" in channel.name or info["duration"] < 120:
            unique = False
        else:
            unique = True

        vid = VideoModel.create(
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

        return VideoItem.from_model(vid)

    @staticmethod
    def grab_info_from_youtube(youtube_id):
        info, files = get_video_info(youtube_id=youtube_id, output_folder=WORKING)
        return info

    @staticmethod
    def refresh_youtube_info(video_id):
        vid = VideoModel.get(VideoModel.id == video_id)
        FileManager.remove_existing_files(
            video_id, vid.youtube_id, ["info", "subtitle", "poster"]
        )
        info, files = get_video_info(youtube_id=vid.youtube_id, output_folder=WORKING)

        vid.title = info["title"]
        vid.url = info["webpage_url"]
        vid.upload_date = info["upload_date"]
        vid.duration = info["duration"]
        vid.description = info["description"]
        vid.save()

        for file in files:
            logger.debug(
                f"Processing files in VideoItem.create_from_youtube_id: {file}"
            )
            FileManager.add_path_to_video(file, vid)
        return vid

    @staticmethod
    def download_video_from_youtube(video_id):
        vid = VideoModel.get(VideoModel.id == video_id)
        FileManager.remove_existing_files(video_id, vid.youtube_id, ["video", "audio"])
        info, files = download_video_file(vid.youtube_id, WORKING, progress_hook=None)
        for file in files:
            logger.debug(
                f"Processing files in VideoItem.download_video_from_youtube: {file}"
            )
            FileManager.add_path_to_video(file, vid)

    @staticmethod
    def get_details_for_video(id: int):
        vid = (
            VideoModel.select(
                VideoModel,
                YoutubeSeries,
                Channel,
                AlbumModel,
                Series,
                SectionModel,
            )
            .join(
                YoutubeSeries,
                peewee.JOIN.LEFT_OUTER,
                on=(VideoModel.youtube_series_id == YoutubeSeries.id),
            )
            .switch(VideoModel)
            .join(Channel)
            .switch(VideoModel)
            .join(
                AlbumModel,
                peewee.JOIN.LEFT_OUTER,
                on=(VideoModel.album_id == AlbumModel.id),
            )
            .switch(VideoModel)
            .join(Series, peewee.JOIN.LEFT_OUTER)
            .switch(VideoModel)
            .join(
                SectionModel,
                peewee.JOIN.LEFT_OUTER,
                on=(VideoModel.id == SectionModel.video_id),
            )
            .where(VideoModel.id == id)
        ).get()
        return VideoItem.from_model(vid)

    def update_from_youtube(self):
        # download files to temp folder
        info, files = get_video_info(youtube_id=self.youtube_id, output_folder=WORKING)

        # logger.debug(f"Info: {info}")
        # logger.debug(f"Files: {files}")
        vid = VideoModel.select().where(VideoModel.id == self.id).get()
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
        VideoItem.create_xml_for_jellyfin(self.id)
        logger.success(f"Grabbed metadata for {vid.title} from youtube")

    def process_downloaded_files(self, files):
        logger.debug("🧪🧪🧪🧪🧪does this still happen 10-26-24")
        logger.debug(f"Processing downloaded files for {self.title}")
        for downloaded_file in files:
            if downloaded_file.suffix == ".webp":
                converted = convert_webp_to_png(downloaded_file)
                Path(downloaded_file).unlink()
                files.pop(files.index(downloaded_file))
                files.append(converted)
                downloaded_file = converted

            existing = (
                FileItem.select()
                .where(FileItem.filename == downloaded_file.name)
                .get_or_none()
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

        vid = VideoModel.select().where(VideoModel.id == self.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)
        refresh_library()

    def save_to_database(self):
        logger.debug(f"Not sure if this is used 🧪🧪🧪🧪🧪🧪 10/26/24")
        vid = VideoModel.select().where(VideoModel.id == self.id).get()
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

    @staticmethod
    def create_xml_for_jellyfin(video_id):
        vid = VideoModel.get(VideoModel.id == video_id)
        album_data = {
            "lockdata": False,
            "track_position": 0,
            "dateadded": datetime.now().isoformat(),
            "title": vid.title,
            "track_title": vid.title,
            "sorttitle": vid.title,
            "year": vid.upload_date.year,
            "runtime": int(vid.duration / 60),  # rounded minutes
            "poster": f"/data/music1/inputs/Harry Mack/{vid.youtube_id}/poster.webp",
            "track_duration": "21:45",  # this is in minutes:seconds format. what happens if longer than 60 minutes?
        }

        try:
            create_album_xml(WORKING / "album.nfo", album_data)
            return WORKING / "album.nfo"
        except Exception as e:
            logger.error(f"Error creating album xml: {e}")
            return None

    def create_album_nfo(self):

        FileManager.remove_existing_files(self.id, self.youtube_id, ["album_nfo"])

        new_file = VideoItem.create_xml_for_jellyfin(self.id)
        FileManager.add_path_to_video(new_file, self)
