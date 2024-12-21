from hmtc.models import Video as VideoModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.models import YoutubeSeriesVideo as YoutubeSeriesVideoModel
from hmtc.repos.base_repo import Repository


def YoutubeSeriesRepo():
    return Repository(
        model=YoutubeSeriesModel,
        label="YoutubeSeries",
    )
