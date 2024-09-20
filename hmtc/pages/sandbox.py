from loguru import logger
from typing import Callable
import solara
from pathlib import Path
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem
import PIL
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
        album = AlbumModel.get_by_id(2465)
        poster = FileManager.get_file_for_album(album, "poster")
        if poster is None:
            solara.Text("No poster")
            return
        image = PIL.Image.open(Path(str(poster)))
        solara.Image(image, width="700px")
