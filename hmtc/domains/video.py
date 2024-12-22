from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Video as VideoModel
from hmtc.repos.video_repo import VideoRepo
from typing import Dict, Any


class Video(BaseDomain):
    model = VideoModel
    repo = VideoRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "description": self.instance.description,
            "duration": self.instance.duration,
            "upload_date": self.instance.upload_date,
            "url": self.instance.url,
            "youtube_id": self.instance.youtube_id,
            "unique_content": self.instance.unique_content,
            "jellyfin_id": self.instance.jellyfin_id,
            "channel_id": self.instance.channel_id,
            "disc_id": self.instance.disc_id,
        }
