from typing import List

from loguru import logger

from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import Album as AlbumModel
from hmtc.models import Channel as ChannelModel
from hmtc.models import Section as SectionModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import Video as VideoModel
from hmtc.models import YoutubeSeries as YoutubeSeriesModel
from hmtc.repos.base_repo import Repository


class Video:
    repo = Repository(model=VideoModel(), label="Video")
    channel_repo = Repository(model=ChannelModel(), label="Channel")

    @classmethod
    def create(cls, data) -> VideoModel:
        channel = cls.channel_repo.get(id=data["channel_id"])
        data["channel"] = channel

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
        _dict["channel"] = Channel.serialize(item.channel.id)
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
        from hmtc.domains.section import Section
        from hmtc.domains.superchat import Superchat

        sections = SectionModel.select().where(SectionModel.video_id == item_id)

        for section in sections:
            Section.delete_id(section.id)

        superchats = SuperchatModel.select().where(SuperchatModel.video_id == item_id)
        for superchat in superchats:
            Superchat.delete_id(superchat.id)

        cls.repo.delete_by_id(item_id=item_id)

    @classmethod
    def unique_count(cls) -> int:
        return VideoModel.select().where(VideoModel.unique_content == True).count()
