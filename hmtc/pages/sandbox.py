from loguru import logger
from typing import Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import (
    Video as VideoModel,
    Channel,
    Series,
    YoutubeSeries,
    Playlist,
    Album as AlbumModel,
)
import peewee
from hmtc.utils.my_jellyfin_client import MyJellyfinClient


@solara.component_vue("../components/shared/snackbar.vue", vuetify=True)
def Sandbox(show: bool, color: str, message: str, icon: str):
    pass


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    with solara.Column(classes=["main-container"]):
        Sandbox(show=True, color="green", message="Hello World", icon="mdi-album")
