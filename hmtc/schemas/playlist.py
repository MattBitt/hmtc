import dataclasses

from loguru import logger

from hmtc.models import Playlist, Video
from hmtc.schemas.base import BaseItem


@dataclasses.dataclass(frozen=True)
class PlaylistItem(BaseItem):

    title: str = None
    url: str = None
    youtube_id: str = None
    enabled: bool = False
    has_chapters: bool = False
    last_update_completed = None
    album_per_episode: bool = False
    enable_video_downloads: bool = False
    contains_unique_content: bool = False
    db_model = Playlist

    @classmethod
    def count_unique(cls, unique: bool = True):
        return (
            Playlist.select().where(Playlist.contains_unique_content == unique).count()
        )

    @classmethod
    def grab_page_from_db(
        cls, current_page, per_page, text_search=None, sort_column=None, sort_order=None
    ):
        query = Playlist.select()

        if text_search:
            query = query.where(
                (Playlist.title.contains(text_search))
                | (Playlist.url.contains(text_search))
                | (Playlist.youtube_id.contains(text_search))
            )

        sort_field = None

        if sort_column is not None:
            sort_field = cls.get_sort_field(sort_column, sort_order)

        if sort_field is not None:
            items = query.order_by(sort_field)
        else:
            items = query.order_by(Playlist.title.asc())

        if not items:
            logger.error("no items found")
            return [], 0

        total_items = items.count()
        query = items.paginate(current_page, per_page)
        page_of_items = [
            PlaylistItem(
                title=item.title,
                url=item.url,
                id=item.id,
                youtube_id=item.youtube_id,
                enabled=item.enabled,
                album_per_episode=item.album_per_episode,
                enable_video_downloads=item.enable_video_downloads,
                contains_unique_content=item.contains_unique_content,
            )
            for item in query
        ]
        return page_of_items, total_items

    def db_object(self):
        return Playlist.get_or_none(Playlist.id == self.id)

    def save_to_db(self):
        logger.debug(f"Saving to db: {self}")
        if self.id is None:
            existing = Playlist.get_or_none(Playlist.youtube_id == self.youtube_id)
            if not existing:
                Playlist.create(
                    title=self.title,
                    youtube_id=self.youtube_id,
                    enabled=self.enabled,
                    manual=True,
                )
            else:
                logger.info(
                    f"Playlist with youtube_id {self.youtube_id} already exists"
                )
        else:
            Playlist.update(
                title=self.title, youtube_id=self.youtube_id, enabled=self.enabled
            ).where(Playlist.id == self.id).execute()

    def count_videos(self, no_duration=False):
        query = Video.select().join(Playlist).where(Video.playlist_id == self.id)
        if no_duration:
            query = query.where(Video.duration.is_null())
        return len(list(query))

    @staticmethod
    def create_from_youtube_id(youtube_id):
        # for now can't actually do this
        # some problem with the ffmpeg function
        # i had to download and create the info file manually
        raise DeprecationWarning("Can't create playlist from youtube_id automatically")

    def update_from_youtube(self):
        vids = Video.select().join(Playlist).where(Video.playlist_id == self.id)
        for vid in vids:
            vid.update_from_yt()

    def videos(self):
        return Video.select().join(Playlist).where(Video.playlist_id == self.id)
