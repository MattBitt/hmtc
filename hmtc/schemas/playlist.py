import dataclasses

from loguru import logger

from hmtc.models import Playlist, Video


def get_sort_field(cls, sort_column, sort_order):
    if sort_column not in cls.db_model._meta.fields:
        logger.error(f"unknown sort column: {sort_column}")
        raise Exception("unknown sort column")

    field = getattr(Playlist, sort_column)

    if sort_order != "asc":
        field = field.desc()
    return field


# our model for a todo item, immutable/frozen avoids common bugs
@dataclasses.dataclass(frozen=True)
class PlaylistItem:
    id: int = None
    title: str = None
    url: str = None
    youtube_id: str = None
    enabled: bool = True
    last_update_completed = None
    album_per_episode: bool = False
    enable_video_downloads: bool = False
    contains_unique_content: bool = False
    db_model = Playlist

    @classmethod
    def count_enabled(cls, enabled: bool = True):
        return Playlist.select().where(Playlist.enabled == enabled).count()

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
            sort_field = get_sort_field(cls, sort_column, sort_order)

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

    @classmethod
    def grab_id_from_db(cls, id: int):
        item = Playlist.get_or_none(Playlist.id == id)
        return item

    @classmethod
    def grab_by_youtube_id(cls, youtube_id: str):
        item = cls.db_model.get_or_none(cls.db_model.youtube_id == youtube_id)
        return item

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

    def count_videos(self):

        videos = Video.select().join(Playlist).where(Video.playlist_id == self.id)
        return len(videos)

    def get_poster(self):
        playlist = Playlist.select().where(Playlist.id == self.id).get()
        return playlist.poster

    @staticmethod
    def create_from_youtube_id(youtube_id):
        # for now can't actually do this
        # some problem with the ffmpeg function
        # i had to download and create the info file manually
        raise DeprecationWarning("Can't create playlist from youtube_id automatically")
