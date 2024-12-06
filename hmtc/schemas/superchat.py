from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from loguru import logger

from hmtc.models import File as FileModel
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.schemas.superchat_segment import SuperchatSegment
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_manager import ImageManager


@dataclass(kw_only=True)
class Superchat:

    frame_number: int
    id: int
    video: VideoItem = None
    segment: SuperchatSegment = None
    files: list = field(default_factory=list)
    im: ImageManager = None
    image_file: Path = None

    def __post_init__(self):
        if self.id is not None:
            _image_file = (
                SuperchatFileModel.select()
                .where(
                    (SuperchatFileModel.superchat_id == self.id)
                    & (SuperchatFileModel.file_type == "image")
                )
                .get_or_none()
            )
            if _image_file is not None:
                self.image_file = Path(_image_file.path) / _image_file.filename

    @staticmethod
    def from_model(superchat: SuperchatModel) -> "Superchat":

        return Superchat(
            id=superchat.id,
            frame_number=superchat.frame_number,
            video=superchat.video,
            segment=superchat.segment,
            files=superchat.files,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "frame_number": self.frame_number,
            "video": self.video.serialize(),
            "segment": self.segment.serialize(),
            "files": [f.serialize() for f in self.files],
        }

    @staticmethod
    def delete_id(item_id):
        superchat = SuperchatModel.get_by_id(item_id)
        sc_file = SuperchatFileModel.get_or_none(superchat_id=superchat.id)

        if sc_file is not None:
            try:
                (Path(sc_file.path) / sc_file.filename).unlink()
            except FileNotFoundError:
                logger.debug(
                    f"Error: Could not find file {sc_file.filename}. But we are trying to delete it anyway."
                )
            sc_file.delete_instance()
        if superchat.segment is not None:
            SuperchatSegment.delete_id(superchat.segment.id)
        superchat.delete_instance()

    def delete_me(self):
        self.delete_id(self.id)

    def save_to_db(self) -> None:
        if self.id is None:
            sc = SuperchatModel(
                frame_number=self.frame_number,
                video_id=self.video.id,
            )
            sc.save()
            self.id = sc.id
        else:
            sc = SuperchatModel.get_by_id(self.id)
            sc.frame_number = self.frame_number
            sc.video_id = self.video.id
            sc.save()

    def get_image(self):
        if self.image_file is None:
            raise ValueError("No image file associated with this superchat")

        if self.im is None:
            self.im = ImageManager(self.image_file)

        return self.im.image

    def add_image(self, new_path) -> None:
        if isinstance(new_path, Path):
            path = new_path
            if path.parent is None or "videos/None" in str(path.parent):
                raise ValueError(
                    f"Path must have a parent directory not {type(path.parent)}. This is thie bug!!!💡💡💡💡"
                )
            image_db_file = SuperchatFileModel(
                superchat_id=self.id,
                path=path.parent,
                filename=path.name,
                file_type="image",
            )
            image_db_file.save()
        elif isinstance(new_path, np.ndarray):
            vid_file_path = (
                FileModel.select()
                .where(
                    (FileModel.video_id == self.video.id)
                    & (FileModel.file_type == "video")
                )
                .get()
            )
            image_file_path = (
                Path(vid_file_path.path) / "superchats" / f"{self.frame_number}.jpg"
            )

            self.im = ImageManager(new_path)
            self.im.save_image(image_file_path)
            self.image_file = image_file_path
            if image_file_path.parent is None or "videos/None" in str(
                image_file_path.parent
            ):
                raise ValueError(
                    f"image_file_path must have a parent directory not {type(image_file_path.parent)}. This is thie bug!!!☹️☹️☹️☹️☹️"
                )
            image_db_file = SuperchatFileModel(
                superchat_id=self.id,
                path=image_file_path.parent,
                filename=image_file_path.name,
                file_type="image",
            )
            image_db_file.save()
        else:
            raise TypeError(
                f"Image must be a file path or a numpy array. Got {type(new_path)}"
            )

    def write_image(self, filename, new_path: Path = None) -> None:
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
        self.im.save_image(new_path / filename)
