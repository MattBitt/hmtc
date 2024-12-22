from typing import Any, Dict

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.series_repo import SeriesRepo
from hmtc.repos.youtube_series_repo import YoutubeSeriesRepo


class YoutubeSeries(BaseDomain):
    model = YoutubeSeriesModel
    repo = YoutubeSeriesRepo()
    series_repo = SeriesRepo()

    def serialize(self) -> Dict[str, Any]:
        series = self.series_repo.get_by_id(self.instance.series_id)
        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "series": series.my_dict(),
        }
