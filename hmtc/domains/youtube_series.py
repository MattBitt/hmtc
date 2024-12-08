from typing import List

from loguru import logger

from hmtc.repos.base_repo import Repository
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.models import Series as SeriesModel
from hmtc.domains.series import Series


class YoutubeSeries:
    repo = Repository(model=YoutubeSeriesModel(), label="Youtube Series")
    series_repo = Repository(model=SeriesModel(), label="Series")

    @classmethod
    def create(cls, data) -> YoutubeSeriesModel:
        series = cls.series_repo.get(title=data["series"])
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

        series = Series.serialize(item.series.id)

        _dict = item.my_dict()
        _dict["series"] = series["title"]

        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
