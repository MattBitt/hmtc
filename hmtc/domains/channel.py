import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List

from loguru import logger

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.repos.base_repo import Repository
from hmtc.models import db_null
from hmtc.models import Channel as ChannelModel

config = init_config()
db = init_db(db_null, config)


class Channel:
    model = ChannelModel()
    repo = Repository(model=model, label="Channel")

    @classmethod
    def create(cls, data) -> ChannelModel:
        new_channel = cls.repo.create_item(data=data)
        return new_channel

    @classmethod
    def load(cls, item_id) -> ChannelModel:
        _item = cls.repo.load_item(item_id=item_id)
        return _item

    @classmethod
    def update(cls, item_id, data) -> ChannelModel:
        _item = cls.repo.update_item(item_id=item_id, data=data)
        return _item

    def get_all(self) -> List[ChannelModel]:
        return list(self.repo.get_all())

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)
        logger.success(f"Deleted !")

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        return item.simple_dict()

    @staticmethod
    def get_by_id(item_id) -> ChannelModel:
        return ChannelModel.get_by_id(item_id)

    @staticmethod
    def last_update_completed() -> str | None:
        channel = (
            (
                ChannelModel.select(ChannelModel.last_update_completed).where(
                    ChannelModel.auto_update == True
                )
            )
            .order_by(ChannelModel.last_update_completed.desc())
            .limit(1)
            .get_or_none()
        )
        if channel:
            return str(channel.last_update_completed)

        return None

    @classmethod
    def to_auto_update(cls):
        channels = ChannelModel.select().where(ChannelModel.auto_update == True)
        for channel in channels:
            yield channel
        else:
            return None
