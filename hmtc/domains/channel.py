import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List

from loguru import logger

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base import Repository
from hmtc.models import db_null
from hmtc.models import Channel as ChannelModel

config = init_config()
db = init_db(db_null, config)


@dataclass()
class Channels:
    model: ChannelModel = field(default_factory=ChannelModel)
    model_verbose: str = field(default="Channel")
    _id: int = field(default=None)

    def __post_init__(self):
        self._id = self.model.id or None

    def create(self, data) -> "Channels":
        _item = Repository.create_from_dict(model=self.model, data=data)
        return Channels(model=_item)

    def load(self, _id) -> "Channels":
        _item = Repository.load_by_id(model=self.model, _id=_id)
        return Channels(model=_item)

    def update(self, data):
        _item = Repository.update_from_dict(model=self.model, _id=self._id, data=data)
        return Channels(model=_item)

    def get_all(self) -> List["Channels"]:
        return Repository.get_all(model=self.model)

    def delete_me(self) -> None:
        if self._id is None:
            logger.error(f"Need to load data before deleting")
            item = self.load(self.model.id)

        Repository.delete_by_id(model=self.model, _id=self._id)
        logger.success(f"Deleted !")

    def serialize(self) -> dict:
        return asdict(self).pop("model").simple_dict()

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
            yield cls(channel)
        else:
            return None
