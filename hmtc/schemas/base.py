from dataclasses import dataclass

from loguru import logger


@dataclass(frozen=True, kw_only=True)
class BaseItem:
    id: int = None
    enabled: bool = True
    item_type: str = "BASE"

    @classmethod
    def count_enabled(cls, enabled: bool = True):
        logger.debug(
            f"🧪🧪🧪🧪🧪 11-10-2024 Classmethod of BaseItem called, {cls}, count_enabled, {enabled}"
        )
        return cls.db_model.select().where(cls.enabled == enabled).count()

    @classmethod
    def grab_id_from_db(cls, id: int):
        logger.debug(
            f"🧪🧪🧪🧪🧪 11-10-2024 Classmethod of BaseItem called, {cls}, id, {id}"
        )
        item = cls.db_model.get_or_none(cls.db_model.id == id)
        return item

    @classmethod
    def grab_by_youtube_id(cls, youtube_id: str):
        logger.debug(
            f"🧪🧪🧪🧪🧪 11-10-2024 Classmethod of BaseItem called, {cls}, id, {youtube_id}"
        )
        item = cls.db_model.get_or_none(cls.db_model.youtube_id == youtube_id)
        return item

    @classmethod
    def get_sort_field(cls, sort_column, sort_order):
        logger.debug(
            f"🧪🧪🧪🧪🧪 11-10-2024 Classmethod of BaseItem called, {cls}, id, {sort_column}, {sort_order}"
        )
        if sort_column not in cls.db_model._meta.fields:
            logger.error(f"unknown sort column: {sort_column}")
            raise Exception("unknown sort column")

        field = getattr(cls.db_model, sort_column)

        # if sort_order != "asc":
        #     field = field.desc()
        return field

    def get_poster(self):
        logger.debug(f"🧪🧪🧪🧪🧪 11-10-2024 get_poster of BaseItem called, {self}")
        item = self.db_model.select().where(self.db_model.id == self.id).get()
        return item.poster

    def serialize(self):
        logger.error(f"serialize NOT IMPLEMENTED {self.item_type}")
        raise NotImplementedError

    def from_model(self):
        logger.error(f"from_model NOT IMPLEMENTED {self.item_type}")
        raise NotImplementedError

    @staticmethod
    def update_from_dict(item_id, new_data):
        logger.error(f"update_from_dict NOT IMPLEMENTED {item_id} {new_data}")
        raise NotImplementedError

    @staticmethod
    def delete_id(item_id):
        logger.error(f"delete_id NOT IMPLEMENTED {item_id}")
        raise NotImplementedError
