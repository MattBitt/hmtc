from dataclasses import dataclass, field
from pathlib import Path
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.utils.opencv.image_manager import ImageManager


@dataclass
class SuperchatSegment:

    start_time: int
    end_time: int

    id: int = None
    image: ImageManager = None
    next_segment: "SuperchatSegment" = None
    previous_segment: "SuperchatSegment" = None
    video_id: int = None
    track_id: int = None
    files: list = field(default_factory=list)

    @staticmethod
    def from_model(segment: SuperchatSegmentModel) -> "SuperchatSegment":

        image_file = segment.files[0] if segment.files else None

        if image_file:
            image = ImageManager(image_file)
        else:
            image = None
        return SuperchatSegment(
            id=segment.id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            image=image,
            next_segment=segment.next_segment,
            previous_segment=segment.previous_segment,
            video_id=segment.video_id,
            track_id=segment.track_id,
            files=segment.files,
        )

    @staticmethod
    def create_from_superchat(superchat: SuperchatItem) -> "SuperchatSegment":
        ss = SuperchatSegmentModel.create(
            start_time=superchat.frame_number,
            end_time=superchat.frame_number,
            video=superchat.video,
        )
        if superchat.image is None:
            logger.error("IMage is blank here")
            return SuperchatSegment.from_model(ss)
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
        for file in segment.files:
            (Path(file.path) / file.filename).unlink()
            file.delete_instance()
        segment.delete_instance()

    def delete_me(self):
        if self.next_segment is None:
            new_seg_id = None
        else:
            new_seg_id = self.next_segment.id
        leftover = (
            SuperchatSegmentModel.select()
            .where(SuperchatSegmentModel.next_segment == self.id)
            .get_or_none()
        )
        if leftover:
            leftover.next_segment.id = new_seg_id
            leftover.save()
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

    @staticmethod
    def combine_segments(segment1: "SuperchatSegment", segment2: "SuperchatSegment"):
        if segment1.next_segment.id == segment2.id:
            # merging with next segment
            segment2.start_time = segment1.start_time
            _old_prev = segment1.previous_segment.get_or_none()
            if _old_prev is not None:
                _old_prev.next_segment = segment2.id
                _old_prev.save()
            old_file = (
                SuperchatFileModel.select()
                .where(SuperchatFileModel.segment_id == segment1.id)
                .get_or_none()
            )
            if old_file is not None:
                old_file.delete_instance(recursive=True)

            segment1.delete_me()
            segment2.save_to_db()
        else:
            # merging with previous segment
            segment1.end_time = segment2.end_time
            segment1.next_segment = segment2.next_segment
            old_file = (
                SuperchatFileModel.select()
                .where(SuperchatFileModel.segment_id == segment2.id)
                .get_or_none()
            )
            if old_file is not None:
                old_file.delete_instance(recursive=True)
            segment1.save_to_db()

            segment2.delete_me()

    def __repr__(self):
        return f"SuperchatSegmentItem({self.id}, {self.start_time}, {self.end_time})"

    def __str__(self):
        return f"SuperchatSegmentItem({self.id}, {self.start_time}, {self.end_time})"
