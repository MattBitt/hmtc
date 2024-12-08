from typing import List

from loguru import logger

from hmtc.repos.base_repo import Repository
from hmtc.models import Channel as ChannelModel


class Channel:
    model = ChannelModel()
    repo = Repository(model=model, label="Channel")

    @classmethod
    def create(cls, data) -> ChannelModel:
        return cls.repo.create_item(data=data)

    @classmethod
    def load(cls, item_id) -> ChannelModel:
        return cls.repo.load_item(item_id=item_id)

    @classmethod
    def update(cls, data) -> ChannelModel:
        return cls.repo.update_item(data=data)

    @classmethod
    def get_all(cls) -> List[ChannelModel]:
        return list(cls.repo.get_all())

    @classmethod
    def serialize(cls, item_id) -> dict:
        item = cls.load(item_id)
        return item.my_dict()

    @classmethod
    def delete_id(cls, item_id) -> None:
        cls.repo.delete_by_id(item_id=item_id)

    @staticmethod
    def last_update_completed() -> str | None:
        channel = (
            ChannelModel.select(ChannelModel.last_update_completed)
            .where(ChannelModel.auto_update == True)
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
