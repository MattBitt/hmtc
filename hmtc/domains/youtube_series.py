from typing import List

from loguru import logger

from hmtc.domains.series import Series
from hmtc.models import Series as SeriesModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.base_repo import Repository
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo


class YoutubeSeries:
    repo = YoutubeSeriesRepo()
    series_repo = Repository(model=SeriesModel(), label="Series")

    @classmethod
    def create(cls, data) -> YoutubeSeriesModel:
        series = cls.series_repo.get(id=data["series_id"])
        data["series"] = series
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> YoutubeSeriesModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> YoutubeSeriesModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[YoutubeSeriesModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["series"] = Series.serialize(item.series.id)
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
