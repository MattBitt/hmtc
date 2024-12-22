from pathlib import Path
from typing import Any, Dict

from peewee import ModelSelect

from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFile as VideoFileModel
from hmtc.repos.video_repo import VideoRepo
from hmtc.utils.file_manager import FileManager

config = init_config()

STORAGE = Path(config["STORAGE"]) / "videos"


class Video(BaseDomain):
    model = VideoModel
    repo = VideoRepo()
    fm = FileManager(
        model=VideoFileModel,
        filetypes=["poster", "thumbnail", "info", "audio", "video", "subtitles"],
        path=STORAGE,
    )

    def serialize(self) -> Dict[str, Any]:
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
            "disc_id": self.instance.disc_id,
            "file_count": len(self.fm.files(self.instance.id)),
        }

    @classmethod
    def latest(cls, limit: int) -> ModelSelect:
        return (
            cls.repo.model.select()
            .order_by(cls.repo.model.upload_date.desc())
            .limit(limit)
        )
