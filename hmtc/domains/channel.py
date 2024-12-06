from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from loguru import logger
from hmtc.domains.base import BaseDomain
from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.models import Channel as ChannelModel
from hmtc.models import db_null


config = init_config()
db = init_db(db_null, config)


@dataclass(frozen=True, kw_only=True)
class Channel(BaseDomain):
    channel: ChannelModel

    @classmethod
    def create_from_dict(cls, new_data) -> "Channel":
        try:
            _channel = ChannelModel.create(
                title=new_data["title"],
                url=new_data["url"],
                youtube_id=new_data["youtube_id"],
                auto_update=new_data["auto_update"],
                last_update_completed=new_data["last_update_completed"],
            )
        except Exception as e:
            logger.error(f"Error {e} creating channel {new_data}")
            raise e

        return cls(channel=_channel)

    def serialize(self) -> dict:
        _dict = asdict(self)
        model = _dict.pop("channel")
        return model

    def delete_me(self) -> None:
        self.channel.delete_instance()

    @staticmethod
    def get_auto_update_channels():
        for channel in ChannelModel.select().where(ChannelModel.auto_update == True):
            yield Channel(channel=channel)

    @staticmethod
    def get_all():
        for channel in ChannelModel.select():
            yield Channel(channel=channel)
