from loguru import logger
from typing import Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel, Channel, Series, YoutubeSeries, Playlist
import peewee
from hmtc.utils.my_jellyfin_client import MyJellyfinClient


@solara.component_vue("sandbox.vue", vuetify=True)
def Sandbox(items: list = []):
    pass


@solara.component_vue("../components/album/album_selector.vue", vuetify=True)
def AlbumSelector(states: list = [], event_save_album: Callable = None):
    pass


def save_album(album):
    logger.debug(f"Saving Album: {album}")


@solara.component
def Page():
    (
        VideoModel.select(
            VideoModel.upload_date,
            YoutubeSeries,
            VideoModel.episode,
            VideoModel.title,
            VideoModel.youtube_id,
            VideoModel.duration,
            Channel,
            Series,
            Playlist,
            VideoModel.id,
            VideoModel.contains_unique_content,
        )
        .join(Channel, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(Series)
        .switch(VideoModel)
        .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(Playlist, peewee.JOIN.LEFT_OUTER)
    )
    MySidebar(router=solara.use_router())

    with solara.Column(classes=["main-container"]):
        AlbumSelector(states=["matt", "lindsay", "walle"], event_save_album=save_album)
