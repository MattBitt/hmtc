from dataclasses import dataclass
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.models import SuperchatFile as SuperchatFileModel


@dataclass
class SuperchatSegment:

    start_time: int
    end_time: int
    image_file_id: int = 0
    id: int = None
    image: ImageManager = None

    @staticmethod
    def from_model(segment: SuperchatSegmentModel) -> "SuperchatSegment":
        image_file = SuperchatFileModel.get_by_id(segment.image_file_id)
        image = ImageManager(image_file)
        return SuperchatSegment(
            id=segment.id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            image_file_id=segment.image_file_id,
            image=image,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "image_file_id": self.image_file_id,
        }

    @staticmethod
    def delete_id(item_id):
        segment = SuperchatSegmentModel.get_by_id(item_id)
        segment.delete_instance(recursive=True)

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
        segment1.save()
        segment2.delete_instance(recursive=True)
        return segment1
