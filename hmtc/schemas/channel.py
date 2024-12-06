import dataclasses
from datetime import datetime

from loguru import logger

from hmtc.models import Channel as ChannelModel
from hmtc.schemas.base import BaseItem


@dataclasses.dataclass(frozen=True, kw_only=True)
class Channel(BaseItem):
    name: str
    url: str = None
    youtube_id: str = None
    id: int = None
    last_update_completed: datetime = None

    @staticmethod
    def from_model(channel: ChannelModel) -> "Channel":
        return Channel(
            id=channel.id,
            name=channel.name,
            url=channel.url,
            youtube_id=channel.youtube_id,
            last_update_completed=channel.last_update_completed,
        )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "youtube_id": self.youtube_id,
            "last_update_completed": self.last_update_completed,
        }

    def update_from_dict(channel_id, new_data) -> None:
        channel = ChannelModel.get_by_id(channel_id)
        channel.name = new_data["name"]
        channel.url = new_data["url"]
        channel.youtube_id = new_data["youtube_id"]
        channel.save()

    def delete_id(channel_id) -> None:
        channel = ChannelModel.get_by_id(channel_id)
        channel.delete_instance()

    ## old methods (11-10-24)
    @classmethod
    def grab_n_from_db(cls, n: int = 10):
        items = ChannelModel.select().order_by(ChannelModel.name.asc()).limit(n)
        if not items:
            return []
        return [
            Channel(
                name=item.name,
                url=item.url,
                id=item.id,
                youtube_id=item.youtube_id,
                # last_update_completed=item.last_update_completed,
            )
            for item in items
        ]

    @classmethod
    def grab_id_from_db(cls, id: int):
        item = ChannelModel.get_or_none(ChannelModel.id == id)
        return item

    def db_object(self):
        return ChannelModel.get_or_none(ChannelModel.id == self.id)

    def save_to_db(self):
        logger.debug(f"Saving to db: {self}")
        if self.id is None:
            ChannelModel.create(
                name=self.name,
                youtube_id=self.youtube_id,
                enabled=self.enabled,
                url=self.url,
            )
        else:
            ChannelModel.update(
                name=self.name,
                youtube_id=self.youtube_id,
                url=self.url,
            ).where(ChannelModel.id == self.id).execute()

    def get_poster(self):
        channel = ChannelModel.select().where(ChannelModel.id == self.id).get()
        return channel.poster

    @staticmethod
    def grab_by_youtube_id(youtube_id: str):
        item = ChannelModel.get_or_none(ChannelModel.youtube_id == youtube_id)
        return item
