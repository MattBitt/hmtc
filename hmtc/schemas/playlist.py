import dataclasses

from loguru import logger

from hmtc.models import Playlist


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
    def grab_page_from_db(cls, current_page, per_page):
        items = Playlist.select().order_by(Playlist.title.asc())
        if not items:
            return []
        query = items.paginate(current_page, per_page)
        return [
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
                    title=self.title, youtube_id=self.youtube_id, enabled=self.enabled
                )
            else:
                logger.info(
                    f"Playlist with youtube_id {self.youtube_id} already exists"
                )
        else:
            Playlist.update(
                title=self.title, youtube_id=self.youtube_id, enabled=self.enabled
            ).where(Playlist.id == self.id).execute()

    def get_poster(self):
        playlist = Playlist.select().where(Playlist.id == self.id).get()
        return playlist.poster
