from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Series as SeriesModel
from hmtc.repos.series_repo import SeriesRepo
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo
from typing import List


class Series(BaseDomain):
    model = SeriesModel
    repo = SeriesRepo()
    youtube_series_repo = YoutubeSeriesRepo()

    def serialize(self) -> dict:
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "start_date": str(self.instance.start_date),
            "end_date": str(self.instance.end_date),
        }

    def youtube_serieses(self) -> List[BaseDomain]:
        return self.youtube_series_repo.get_by(series_id=self.instance.id)
