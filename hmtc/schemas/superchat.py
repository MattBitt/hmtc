from dataclasses import dataclass
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.schemas.base import BaseItem
from hmtc.schemas.video import VideoItem
import numpy as np
from hmtc.utils.opencv.image_manager import ImageManager
from pathlib import Path


@dataclass(kw_only=True)
class Superchat:

    start_time: int
    image: np.ndarray = None
    id: int = None
    end_time: int = None
    image: ImageManager = None
    video: VideoItem = None

    def from_model(superchat: SuperchatModel) -> "Superchat":
        return Superchat(
            id=superchat.id,
            start_time=superchat.start_time,
            video=superchat.video,
            end_time=superchat.end_time,
        )

    def update_end_time(self, end_time: int):
        return Superchat(
            id=self.id,
            image=self.image,
            start_time=self.start_time,
            video_id=self.video.id,
            end_time=end_time,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "video": self.video.serialize(),
        }

    def save_to_db(self) -> None:
        sc = SuperchatModel(
            start_time=self.start_time,
            end_time=self.end_time,
            video_id=self.video.id,
        )
        sc.save()
        self.id = sc.id

    def save_image(self, new_path: Path) -> None:
        if self.id is None:
            raise ValueError("Superchat must be saved to the database first")
        self.image.save_image(new_path)
        image_file = SuperchatFileModel(
            superchat_id=self.id,
            path=new_path.parent,
            filename=new_path.name,
            file_type="image",
        )
        image_file.save()
