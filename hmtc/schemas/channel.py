import dataclasses

from loguru import logger

from hmtc.models import Channel


# our model for a todo item, immutable/frozen avoids common bugs
@dataclasses.dataclass(frozen=True)
class ChannelItem:
    name: str
    url: str = None
    youtube_id: str = None
    id: int = None
    enabled: bool = True
    last_update_completed = None

    @classmethod
    def grab_n_from_db(cls, n: int = 10):
        items = Channel.select().order_by(Channel.name.asc()).limit(n)
        if not items:
            return []
        return [
            ChannelItem(
                name=item.name,
                url=item.url,
                id=item.id,
                youtube_id=item.youtube_id,
                enabled=item.enabled,
                # last_update_completed=item.last_update_completed,
            )
            for item in items
        ]

    @classmethod
    def grab_id_from_db(cls, id: int):
        item = Channel.get_or_none(Channel.id == id)
        return item

    def db_object(self):
        return Channel.get_or_none(Channel.id == self.id)

    def save_to_db(self):
        logger.debug(f"Saving to db: {self}")
        if self.id is None:
            Channel.create(
                name=self.name, youtube_id=self.youtube_id, enabled=self.enabled
            )
        else:
            Channel.update(
                name=self.name, youtube_id=self.youtube_id, enabled=self.enabled
            ).where(Channel.id == self.id).execute()

    def get_poster(self):
        channel = Channel.select().where(Channel.id == self.id).get()
        return channel.poster

    @staticmethod
    def grab_by_youtube_id(youtube_id: str):
        item = Channel.get_or_none(Channel.youtube_id == youtube_id)
        return item
