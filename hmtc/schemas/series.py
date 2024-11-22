import datetime
from dataclasses import dataclass

from loguru import logger

from hmtc.models import Series as SeriesModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.base import BaseItem


@dataclass(frozen=True, kw_only=True)
class Series(BaseItem):
    name: str
    item_type: str = "SERIES"
    start_date: datetime.datetime = None
    end_date: datetime.datetime = None
    id: int = None

    @staticmethod
    def from_model(series: SeriesModel) -> "Series":
        return Series(
            id=series.id,
            name=series.name,
            start_date=series.start_date,
            end_date=series.end_date,
        )

    def serialize(self) -> dict:
        if self.start_date is None:
            start_date = None
        else:
            start_date = self.start_date.isoformat()
        if self.end_date is None:
            end_date = None
        else:
            end_date = self.end_date.isoformat()
        return {
            "id": self.id,
            "name": self.name,
            "start_date": start_date,
            "end_date": end_date,
        }

    @staticmethod
    def update_from_dict(series_id, new_data) -> None:
        series = SeriesModel.get_by_id(series_id)
        series.name = new_data["name"]
        series.start_date = new_data["start_date"]
        series.end_date = new_data["end_date"]
        series.save()

    @staticmethod
    def delete_id(series_id) -> None:
        series = SeriesModel.select().where(SeriesModel.id == series_id)
        logger.error(f"Deleting Series {series.name} ")
        series.delete_instance(recursive=True)

    @staticmethod
    def delete_if_unused(series_id) -> None:
        series = SeriesModel.get_by_id(series_id)
        videos = VideoModel.select().where(VideoModel.series_id == series_id)
        if len(videos) == 0:
            logger.error(f"Series {series.name} not in use. Deleting")
            series.delete_instance()
        else:
            logger.error(f"Series {series.name} in use. Not deleting")
            return False
        return True
