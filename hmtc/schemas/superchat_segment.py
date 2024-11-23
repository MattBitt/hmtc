from dataclasses import dataclass
from hmtc.models import SuperchatSegment as SuperchatSegmentModel


@dataclass
class SuperchatSegment:
    start_time: int
    end_time: int
    image_file_id: int = 0

    @staticmethod
    def from_model(segment: SuperchatSegmentModel) -> "SuperchatSegment":
        return SuperchatSegment(
            start_time=segment.start_time,
            end_time=segment.end_time,
            image_file_id=segment.image_file_id,
        )

    def serialize(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "image_file_id": self.image_file_id,
        }

    @staticmethod
    def delete_id(item_id):
        segment = SuperchatSegmentModel.get_by_id(item_id)
        segment.delete_instance()

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
        ss = SuperchatSegment(
            start_time=segment1.start_time,
            end_time=segment2.end_time,
            image_file_id=segment1.image_file_id,
        )
        ss.save_to_db()
        segment1.delete_instance()
        segment2.delete_instance()
        return ss
