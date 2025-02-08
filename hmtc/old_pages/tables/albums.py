import time
from datetime import date
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.album_table import AlbumTable
from hmtc.domains.album import Album
from hmtc.models import Album as AlbumModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")


def view_details(router, item):
    router.push(f"/domains/album-details/{item['id']}")


@solara.component
def NewAlbum():
    new_item = solara.use_reactive("")
    error = solara.use_reactive("")
    success = solara.use_reactive("")

    def create_album():
        logger.debug(f"Creating new album {new_item.value} if possible")
        if len(new_item.value) <= 1:
            error.set(f"Value {new_item.value} too short.")
        else:
            try:
                new_album = Album.create(
                    {"title": new_item.value, "release_date": date.today()}
                )
                success.set(f"{new_album} was created!")
            except Exception as e:
                error.set(f"Error {e}")

    def reset():
        new_item.set("")
        error.set("")
        success.set("")

    with solara.Card():
        with solara.Columns([6, 6]):
            solara.InputText(label="Album Title", value=new_item)
            with solara.Row():
                solara.Button(
                    label="Create Album", on_click=create_album, classes=["button"]
                )
                solara.Button(label="Reset Form", on_click=reset, classes=["button"])
        if success.value:
            solara.Success(f"{success}")
        elif error.value:
            solara.Error(f"{error}")


@solara.component
def Page():

    router = solara.use_router()

    parse_url_args()

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
        NewAlbum()
        AlbumTable(
            router=router,
            headers=headers,
            base_query=AlbumModel.select(),
            search_fields=search_fields,
        )
