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
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import FileManager

force_update_counter = solara.reactive(0)


def create_query_from_url():
    # url options
    # /albums should be a list of all albums (default)
    # /albums/missing-files/poster should be a list of albums missing poster files

    all = (
        AlbumModel.select(
            AlbumModel,
            fn.COUNT(TrackModel.album_id).coerce(False).alias("track_count"),
        )
        .join(
            TrackModel,
            peewee.JOIN.LEFT_OUTER,
            on=(AlbumModel.id == TrackModel.album_id),
        )
        .group_by(AlbumModel.id)
    )

    router = solara.use_router()

    match router.parts:
        case ["albums"]:
            return all, None, None
        case ["albums", "album", album_id]:
            albums = all.where(AlbumModel.album_id == album_id)
            return albums, "album", album_id
        case ["albums", "missing-files", file_type]:
            if file_type not in ["poster"]:
                logger.error(f"Invalid file type: {file_type}")
                return
            albums_with_files = (
                AlbumModel.select(AlbumModel)
                .join(FileModel, on=(AlbumModel.id == FileModel.album_id))
                .where(FileModel.file_type == file_type)
            )
            all_albums = AlbumModel.select()
            albums = all_albums - albums_with_files
            return albums, "missing-files", file_type

        case _:
            logger.error(f"Invalid URL: {router.url}")


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
def DataTable(items, current_page):
    router = solara.use_router()
    solara.Markdown(f"Page: {current_page}")
    AlbumTable(
        items=items,
        event_save_album=lambda item: logger.debug(f"Saving album {item}"),
        event_delete_album=lambda item: logger.debug(f"Deleting album {item}"),
        event_link1_clicked=lambda item: view_details(router, item),
    )


@solara.component
def Page():
    base_query, filter, id_to_filter = create_query_from_url()
    current_page = solara.use_reactive(1)
    base_query = base_query.paginate(current_page.value, 60)
    router = solara.use_router()
    MySidebar(router)

    items = [
        AlbumItem.from_model(item).serialize()
        for item in base_query.order_by(AlbumModel.id.asc())
    ]

    def previous_page():
        current_page.set(current_page.value - 1)

    def next_page():
        current_page.set(current_page.value + 1)

    with solara.Column(classes=["main-container"]):
        solara.Button("Previous", on_click=previous_page)
        solara.Button("Next", on_click=next_page)
        DataTable(items=items, current_page=current_page)
