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
from hmtc.models import Video as VideoModel

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/album/album_table.vue", vuetify=True)
def AlbumTable(
    items: list = [],
    event_save_album=None,
    event_delete_album: Callable = None,
):
    pass


def delete_album(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    album = AlbumModel.get_by_id(item["id"])
    album.delete_instance()


def save_album(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        album = AlbumModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Album ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        AlbumModel.create(**edited_item)
        return

    album.title = edited_item["title"]
    album.release_date = edited_item["release_date"]
    album.save()
    force_update_counter.set(force_update_counter.value + 1)


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
        .order_by(AlbumModel.title.asc())
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
            event_save_album=save_album,
            event_delete_album=delete_album,
        )
