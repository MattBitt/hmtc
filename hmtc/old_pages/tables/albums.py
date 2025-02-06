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
        AlbumTable(
            router=router,
            headers=headers,
            base_query=AlbumModel.select(),
            search_fields=search_fields,
        )
