from hmtc.repos.base_repo import Repository
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.models import Video as VideoModel


class YoutubeSeriesRepo(Repository):
    def __init__(self):
        super().__init__(model=YoutubeSeriesModel(), label="YoutubeSeries")
