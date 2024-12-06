import dataclasses
import datetime

from loguru import logger

from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.schemas.base import BaseItem
from hmtc.domains.series import Series as SeriesItem


@dataclasses.dataclass(frozen=True, kw_only=True)
class YoutubeSeries(BaseItem):
    title: str
    item_type: str = "YOUTUBE SERIES"
    series: SeriesItem = None
    id: int = None

    @staticmethod
    def from_model(series: YoutubeSeriesModel) -> "YoutubeSeries":
        return YoutubeSeries(
            id=series.id,
            title=series.title,
            series=SeriesItem.from_model(series.series),
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "series": self.series.serialize(),
        }

    def update_from_dict(series_id, new_data) -> None:
        series = YoutubeSeriesModel.get_by_id(series_id)
        series.title = new_data["title"]
        series.save()

    def delete_id(series_id) -> None:
        series = YoutubeSeriesModel.get_by_id(series_id)
        series.delete_instance()

    @staticmethod
    def delete_if_unused(youtube_series_id):
        youtube_series = YoutubeSeriesModel.get_by_id(youtube_series_id)
        if youtube_series.videos.count() == 0:
            youtube_series.delete_instance()
        else:
            logger.error(f"Series {youtube_series.title} has videos, cannot delete")
