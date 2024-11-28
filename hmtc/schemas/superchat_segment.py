from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.utils.opencv.image_manager import ImageManager


@dataclass
class SuperchatSegment:

    start_time: int
    end_time: int

    id: int = None

    im: ImageManager = None
    next_segment: "SuperchatSegment" = None
    previous_segment: "SuperchatSegment" = None
    video_id: int = None
    track_id: int = None
    superchats: list = field(default_factory=list)
    files: list = field(default_factory=list)

    @staticmethod
    def from_model(segment: SuperchatSegmentModel) -> "SuperchatSegment":

        return SuperchatSegment(
            id=segment.id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            next_segment=segment.next_segment,
            previous_segment=segment.previous_segment,
            video_id=segment.video_id,
            track_id=segment.track_id,
            files=segment.files,
            superchats=segment.superchats,
        )

    @staticmethod
    def create_from_superchat(superchat) -> "SuperchatSegment":
        ss = SuperchatSegmentModel.create(
            start_time=superchat.frame_number,
            end_time=superchat.frame_number,
            video=superchat.video,
        )
        sc_model = SuperchatModel.get_by_id(superchat.id)
        sc_model.segment_id = ss.id
        sc_model.save()
        superchat_files = SuperchatFileModel.select().where(
            SuperchatFileModel.superchat_id == superchat.id
        )
        for file in superchat_files:
            if file.file_type == "image":
                file.segment_id = ss.id
                file.save()

        return SuperchatSegment.from_model(ss)

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "next_segment": self.next_segment,
            "video_id": self.video_id,
            "track_id": self.track_id,
        }

    def close_segment(self, end_time: int):
        ss = SuperchatSegmentModel.get_by_id(self.id)
        ss.end_time = end_time
        ss.save()

    def set_next_segment(self, next_segment_id: int):
        ss = SuperchatSegmentModel.get_by_id(self.id)
        ss.next_segment = next_segment_id
        ss.save()

    @staticmethod
    def delete_id(item_id):
        segment = SuperchatSegmentModel.get_by_id(item_id)
        segment.delete_instance()

    def delete_me(self):
        files = SuperchatFileModel.select().where(
            SuperchatFileModel.segment_id == self.id
        )
        for file in files:
            file.segment_id = None
            file.save()

        self.delete_id(self.id)

    def save_to_db(self) -> None:
        segment = SuperchatSegmentModel(
            start_time=self.start_time,
            end_time=self.end_time,
            video_id=self.video_id,
            track_id=self.track_id,
            next_segment=self.next_segment.id if self.next_segment else None,
        )
        segment.save()
        self.id = segment.id
        return self

    def add_superchat(self, superchat):
        SuperchatModel.update(segment_id=self.id).where(
            SuperchatModel.id == superchat.id
        ).execute()
        SuperchatFileModel.update(segment_id=self.id).where(
            SuperchatFileModel.superchat_id == superchat.id
        ).execute()

    def get_image(self):
        if self.im is None:
            image_file = (
                SuperchatFileModel.select()
                .where(
                    (SuperchatFileModel.segment_id == self.id)
                    & (SuperchatFileModel.file_type == "image")
                )
                .get()
            )
            self.im = ImageManager(Path(image_file.path) / image_file.filename)
        if self.im is None:
            raise ValueError("Image not found. Please add an image to the superchat.")
        return self.im.image

    @property
    def duration(self):
        return self.end_time - self.start_time
