import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.album import Album as AlbumItem

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/album/album_table.vue", vuetify=True)
def AlbumTable(
    items: list = [],
    event_save_album=None,
    event_delete_album: Callable = None,
    event_link1_clicked: Callable = None,
):
    pass


def view_details(router, item):
    router.push(f"/album-details/{item['id']}")


@solara.component
def Page():
    base_query = (
        AlbumModel.select(
            AlbumModel.id,
            AlbumModel.title,
            AlbumModel.release_date,
            fn.COUNT(VideoModel.album_id).coerce(False).alias("video_count"),
        )
        .join(VideoModel, peewee.JOIN.LEFT_OUTER)
        .group_by(AlbumModel.id, AlbumModel.title)
        .order_by(AlbumModel.id.desc())
    )

    router = solara.use_router()
    MySidebar(router)

    ipyvue.register_component_from_file(
        "MyFirst", "../components/album/myfirst.vue", __file__
    )

    items = pd.DataFrame([item.model_to_dict() for item in base_query]).to_dict(
        "records"
    )
    with solara.Column(classes=["main-container"]):
        AlbumTable(
            items=items,
            event_save_album=lambda x: AlbumItem.save_album(x),
            event_delete_album=lambda x: AlbumItem.delete_album(x),
            event_link1_clicked=lambda x: view_details(router, x),
        )
