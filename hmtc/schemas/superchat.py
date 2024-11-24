from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import numpy as np

from hmtc.models import File as FileModel
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.schemas.base import BaseItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_manager import ImageManager


@dataclass(kw_only=True)
class Superchat:

    frame_number: int
    image: np.ndarray = None
    id: int = None
    video: VideoItem = None

    @staticmethod
    def from_model(superchat: SuperchatModel) -> "Superchat":
        i = (
            SuperchatFileModel.select()
            .where(SuperchatFileModel.superchat_id == superchat.id)
            .get_or_none()
        )
        if i is None:
            logger.error(f"No image found for superchat {superchat.id}")
            return Superchat(
                id=superchat.id,
                frame_number=superchat.frame_number,
                video=VideoItem.from_model(superchat.video),
            )
        im = ImageManager(Path(i.path) / i.filename)
        return Superchat(
            id=superchat.id,
            frame_number=superchat.frame_number,
            video=superchat.video,
            image=im.image,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "frame_number": self.frame_number,
            "video": self.video.serialize(),
        }

    @staticmethod
    def delete_id(item_id):
        superchat = SuperchatModel.get_by_id(item_id)
        sc_file = SuperchatFileModel.get_or_none(superchat_id=superchat.id)
        if sc_file is not None:
            (Path(sc_file.path) / sc_file.filename).unlink()
            sc_file.delete_instance()

        superchat.delete_instance()

    def delete_me(self):
        self.delete_id(self.id)

    def save_to_db(self) -> None:
        sc = SuperchatModel(
            frame_number=self.frame_number,
            video_id=self.video.id,
        )
        sc.save()
        self.id = sc.id

    def get_image(self) -> ImageManager:
        if self.image is None:
            image_file = (
                SuperchatFileModel.select()
                .where(
                    (SuperchatFileModel.superchat_id == self.id)
                    & (SuperchatFileModel.file_type == "image")
                )
                .get()
            )
            self.image = ImageManager(Path(image_file.path) / image_file.filename).image
        return self.image

    def write_image(self, filename, new_path: Path = None) -> None:
        if self.id is None:
            raise ValueError("Superchat must be saved to the database first")
        if self.image is None:
            raise ValueError("Superchat image must be SET before saving")
        if new_path is None:
            vid_file = (
                FileModel.select()
                .where(
                    (FileModel.video_id == self.video.id)
                    & (FileModel.file_type == "video")
                )
                .get()
            )
            new_path = Path(vid_file.path) / "superchats"
            new_path.mkdir(exist_ok=True)

        image_db_file = SuperchatFileModel(
            superchat_id=self.id,
            path=new_path,
            filename=filename,
            file_type="image",
        )
        image_db_file.save()
        ImageManager(self.image).save_image(new_path / filename)

    def __repr__(self):
        return f"<Superchat {self.id} - Frame {self.frame_number}>"

    def __str__(self):
        return f"Superchat {self.id} - Frame {self.frame_number}"
