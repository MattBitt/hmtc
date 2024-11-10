import dataclasses
import datetime

from loguru import logger

from hmtc.models import Series as SeriesModel
from hmtc.schemas.base import BaseItem


@dataclasses.dataclass(frozen=True, kw_only=True)
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

    def update_from_dict(series_id, new_data) -> None:
        series = SeriesModel.get_by_id(series_id)
        series.name = new_data["name"]
        series.url = new_data["url"]
        series.youtube_id = new_data["youtube_id"]
        series.enabled = new_data["enabled"]
        series.save()

    def delete_id(series_id) -> None:
        series = SeriesModel.get_by_id(series_id)
        series.delete_instance()
