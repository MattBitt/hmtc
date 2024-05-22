from dataclasses import dataclass
from loguru import logger


@dataclass(frozen=True, kw_only=True)
class BaseItem:
    id: int = None
    enabled: bool = True

    @classmethod
    def count_enabled(cls, enabled: bool = True):
        return cls.db_model.select().where(cls.enabled == enabled).count()

    @classmethod
    def grab_id_from_db(cls, id: int):
        item = cls.db_model.get_or_none(cls.db_model.id == id)
        return item

    @classmethod
    def grab_by_youtube_id(cls, youtube_id: str):
        item = cls.db_model.get_or_none(cls.db_model.youtube_id == youtube_id)
        return item

    def get_poster(self):
        item = self.db_model.select().where(self.db_model.id == self.id).get()
        return item.poster

    @classmethod
    def get_sort_field(cls, sort_column, sort_order):
        if sort_column not in cls.db_model._meta.fields:
            logger.error(f"unknown sort column: {sort_column}")
            raise Exception("unknown sort column")

        field = getattr(cls.db_model, sort_column)

        if sort_order != "asc":
            field = field.desc()
        return field
