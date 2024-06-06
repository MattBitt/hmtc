from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from hmtc.models import Video
from hmtc.schemas.base import BaseItem


@dataclass(frozen=True, kw_only=True)
class VideoItem(BaseItem):
    title: str = None

    youtube_id: str = None
    url: str = None
    last_update_completed = None
    episode: str = None
    upload_date: datetime = None
    duration: int = 0
    description: str = None
    contains_unique_content: bool = False
    has_chapters: bool = False
    manually_edited: bool = False
    db_model = Video
    series_name: str = "Default"
    playlist_name: str = "Default"

    @classmethod
    def count_videos(cls, enabled: bool = True):
        return cls.db_model.select().where(cls.enabled == enabled).count()

    @classmethod
    def count_no_duration(cls):
        return cls.db_model.select().where(cls.db_model.duration.is_null()).count()

    @classmethod
    def grab_page_from_db(
        cls, current_page, per_page, text_search=None, sort_column=None, sort_order=None
    ):
        # sort column is the column 'string' to sort by
        query = cls.db_model.select()

        if text_search:
            query = query.where(
                (cls.db_model.title.contains(text_search))
                | (cls.db_model.url.contains(text_search))
                | (cls.db_model.youtube_id.contains(text_search))
            )

        sort_field = None

        if sort_column is not None:
            sort_field = cls.get_sort_field(sort_column, sort_order)

        if sort_field is not None:
            items = query.order_by(sort_field)
        else:
            items = query.order_by(cls.id.asc())

        if not items:
            logger.error("no items found")
            return [], 0

        total_items = items.count()
        query = items.paginate(current_page, per_page)

        page_of_items = [
            cls(
                title=item.title,
                url=item.url,
                id=item.id,
                youtube_id=item.youtube_id,
                enabled=item.enabled,
                manually_edited=True,
                upload_date=item.upload_date,
                duration=item.duration,
                description=item.description,
                contains_unique_content=item.contains_unique_content,
                has_chapters=item.has_chapters,
                series_name=(
                    item.series.name if item.series else "Default in Constructor"
                ),
                playlist_name=(
                    item.playlist.title if item.playlist else "Default in Constructor"
                ),
            )
            for item in query
        ]
        return page_of_items, total_items

    def db_object(self):
        return self.db_model.get_or_none(self.db_model.id == self.id)

    def save_to_db(self):
        logger.debug(f"Saving to db: {self}")
        url = "https://www.youtube.com/watch?v=" + self.youtube_id
        if self.id is None:
            existing = self.db_model.get_or_none(
                self.db_model.youtube_id == self.youtube_id
            )
            if not existing:

                self.db_model.create(
                    title=self.title,
                    url=url,
                    youtube_id=self.youtube_id,
                    enabled=self.enabled,
                    manually_edited=True,
                    upload_date=self.upload_date,
                    duration=self.duration,
                    description=self.description,
                    contains_unique_content=self.contains_unique_content,
                    has_chapters=self.has_chapters,
                )
            else:
                logger.info(f"Video with youtube_id {self.youtube_id} already exists")
        else:
            logger.debug(f"Updating video with id {self.id}")
            logger.debug(f"Self = {self}")
            self.db_model.update(
                title=self.title,
                youtube_id=self.youtube_id,
                enabled=self.enabled,
                manually_edited=True,
                upload_date=self.upload_date,
                duration=self.duration,
                description=self.description,
                contains_unique_content=self.contains_unique_content,
                has_chapters=self.has_chapters,
                url=url,
            ).where(self.db_model.id == self.id).execute()

    def update_from_youtube(self):
        video = self.db_model.select().where(self.db_model.id == self.id).get()
        video.update_from_yt()
        return video

    @classmethod
    def from_orm(cls, db_object):
        return cls(
            title=db_object.title,
            url=db_object.url,
            id=db_object.id,
            youtube_id=db_object.youtube_id,
            enabled=db_object.enabled,
            manually_edited=True,
            upload_date=db_object.upload_date,
            duration=db_object.duration,
            description=db_object.description,
            contains_unique_content=db_object.contains_unique_content,
            has_chapters=db_object.has_chapters,
        )
