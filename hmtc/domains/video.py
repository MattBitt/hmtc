from typing import List

from loguru import logger
from hmtc.models import Album as AlbumModel
from hmtc.models import Channel as ChannelModel
from hmtc.models import Series as SeriesModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.models import Video as VideoModel
from hmtc.repos.base_repo import Repository
from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.youtube_series import YoutubeSeries


class Video:
    repo = Repository(model=VideoModel(), label="Video")
    series_repo = Repository(model=SeriesModel(), label="Series")
    channel_repo = Repository(model=ChannelModel(), label="Channel")
    album_repo = Repository(model=AlbumModel(), label="Album")
    youtube_series_repo = Repository(model=YoutubeSeriesModel(), label="Youtube Series")

    @classmethod
    def create(cls, data) -> VideoModel:
        album = cls.album_repo.get(title=data["album"])
        data["album"] = album

        channel = cls.channel_repo.get(title=data["channel"])
        data["channel"] = channel

        series = cls.series_repo.get(title=data["series"])
        data["series"] = series

        youtube_series = cls.youtube_series_repo.get(title=data["youtube_series"])
        data["youtube_series"] = youtube_series

        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> VideoModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> VideoModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[VideoModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)

        _dict = item.my_dict()
        _dict["upload_date"] = str(_dict["upload_date"])
        _dict["series"] = Series.serialize(item.series.id)
        _dict["channel"] = Channel.serialize(item.channel.id)
        _dict["album"] = Album.serialize(item.album.id)
        _dict["youtube_series"] = YoutubeSeries.serialize(item.youtube_series.id)
        _dict["section_info"] = (
            {
                "section_count": 789,
                "track_count": 123,
                "my_new_column": 456,
            },
        )
        _dict["sections"] = []
        _dict["superchats_count"] = 123
        _dict["segments_count"] = 456
        return _dict

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
