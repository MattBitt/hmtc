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

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/album/album_table.vue", vuetify=True)
def AlbumTable(
    items: list = [],
    event_save_album=None,
    event_delete_album: Callable = None,
    event_link1_clicked: Callable = None,
):
    pass


def delete_album(item):
    logger.debug(f"Deleting Item received from Vue: {item}")

    album = AlbumModel.get_by_id(item["id"])
    tracks = TrackModel.select().where(TrackModel.album_id == album.id)
    for track in tracks:
        FileManager.delete_track_file(track, "audio")
        FileManager.delete_track_file(track, "lyrics")
        track.delete_instance()
    vids = VideoModel.select().where(VideoModel.album_id == album.id)
    for vid in vids:
        vid.album_id = None
        vid.save()
    FileManager.delete_album_file(album, "poster")
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
        album = AlbumModel.create(**edited_item)

    album.title = edited_item["title"]
    album.release_date = edited_item["release_date"]
    album.save()


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
            event_save_album=save_album,
            event_delete_album=delete_album,
            event_link1_clicked=lambda x: view_details(router, x),
        )
