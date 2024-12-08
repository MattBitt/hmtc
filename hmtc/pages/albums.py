import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.album_table import AlbumTable
from hmtc.domains.album import Album as AlbumItem
from hmtc.models import Album as AlbumModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel


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
            # albums_with_files = (
            #     AlbumModel.select(AlbumModel)
            #     .join(FileModel, on=(AlbumModel.id == FileModel.album_id))
            #     .where(FileModel.file_type == file_type)
            # )
            all_albums = AlbumModel.select()
            # albums = all_albums - albums_with_files
            return albums, "missing-files", file_type

        case _:
            logger.error(f"Invalid URL: {router.url}")


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

    router = solara.use_router()
    MySidebar(router)

    base_query, filter, id_to_filter = create_query_from_url()

    headers = [
        {
            "text": "Release Date",
            "value": "release_date",
            "sortable": True,
            "width": "10%",
        },
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [AlbumModel.title]

    with solara.Column(classes=["main-container"]):
        AlbumTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
