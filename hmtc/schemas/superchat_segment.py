from dataclasses import dataclass
from pathlib import Path
from hmtc.models import SuperchatFile as SuperchatFileModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.utils.opencv.image_manager import ImageManager


@dataclass
class SuperchatSegment:

    start_time: int
    end_time: int

    id: int = None
    image: ImageManager = None
    next_segment: "SuperchatSegment" = None
    video_id: int = None
    track_id: int = None

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
            video_id=segment.video_id,
            track_id=segment.track_id,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "next_segment": self.next_segment,
            "video_id": self.video_id,
            "track_id": self.track_id,
        }

    @staticmethod
    def delete_id(item_id):
        segment = SuperchatSegmentModel.get_by_id(item_id)
        for file in segment.files:
            (Path(file.path) / file.filename).unlink()
            file.delete_instance()
        segment.delete_instance()

    def delete_me(self):
        self.delete_id(self.id)

    def save_to_db(self) -> None:
        segment = SuperchatSegmentModel(
            start_time=self.start_time,
            end_time=self.end_time,
            image_file_id=self.image_file_id,
        )
        segment.save()
        self.id = segment.id
        return self

    @staticmethod
    def combine_segments(
        segment1: SuperchatSegmentModel, segment2: SuperchatSegmentModel
    ):
        segment1.end_time = segment2.end_time
        # still need to assign image and next_segment
        segment1.save()
        segment2.delete_instance()

        return segment1
