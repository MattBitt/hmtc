from hmtc.models import Video as VideoModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.models import YoutubeSeriesVideo as YoutubeSeriesVideoModel
from hmtc.repos.base_repo import Repository


class YoutubeSeriesRepo(Repository):
    def __init__(self):
        super().__init__(model=YoutubeSeriesModel(), label="YoutubeSeries")

    def videos(self):
        return YoutubeSeriesVideoModel.select().where(
            YoutubeSeriesVideoModel.youtube_series_id == self.model.id
        )
