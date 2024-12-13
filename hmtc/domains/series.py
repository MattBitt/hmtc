from typing import List

from loguru import logger

from hmtc.models import Series as SeriesModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.base_repo import Repository


class Series:
    repo = Repository(model=SeriesModel(), label="Series")

    @classmethod
    def create(cls, data) -> SeriesModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> SeriesModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> SeriesModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[SeriesModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        _dict = item.my_dict()
        _dict["start_date"] = str(_dict["start_date"])
        _dict["end_date"] = str(_dict["end_date"])
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        from hmtc.domains.youtube_series import YoutubeSeries

        youtube_serieses = YoutubeSeriesModel.select().where(
            YoutubeSeriesModel.series == item_id
        )
        for youtube_series in youtube_serieses:
            YoutubeSeries.delete_id(youtube_series.id)

        cls.repo.delete_by_id(item_id=item_id)
