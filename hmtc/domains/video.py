from pathlib import Path
from typing import Any, Dict

from loguru import logger
from peewee import ModelSelect, fn
from PIL import Image

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFiles
from hmtc.repos.file_repo import FileRepo
from hmtc.repos.video_repo import VideoRepo

config = init_config()
STORAGE = Path(config["STORAGE"]) / "videos"


class Video(BaseDomain):
    model = VideoModel
    repo = VideoRepo()
    file_repo = FileRepo(VideoFiles)

    def serialize(self) -> Dict[str, Any]:
        dv = (
            DiscVideoModel.select()
            .where(DiscVideoModel.video_id == self.instance.id)
            .get_or_none()
        )
        if dv is not None:
            album_title = dv.disc.album.title
        else:
            album_title = ""

        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "description": self.instance.description,
            "duration": self.instance.duration,
            "upload_date": self.instance.upload_date.isoformat(),
            "url": self.instance.url,
            "youtube_id": self.instance.youtube_id,
            "unique_content": self.instance.unique_content,
            "jellyfin_id": self.instance.jellyfin_id,
            "channel_id": self.instance.channel_id,
            "file_count": self.file_repo.num_files(self.instance.id),
            "album_title": album_title,
            "channel_title": self.instance.channel.title,
        }

    @classmethod
    def latest(cls, limit: int) -> ModelSelect:
        return (
            cls.repo.model.select()
            .where(cls.repo.model.unique_content == True)
            .order_by(cls.repo.model.upload_date.desc())
            .limit(limit)
        )

    def add_file(self, file: Path):
        year = self.instance.upload_date.strftime("%Y")
        target_path = STORAGE / year / self.instance.youtube_id
        new_name = self.instance.youtube_id

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    @classmethod
    def unique_count(cls):
        return (
            VideoModel.select(fn.COUNT(VideoModel.unique_content))
            .where(VideoModel.unique_content == True)
            .scalar()
        )
