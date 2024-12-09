import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.artist_table import ArtistTable
from hmtc.domains.artist import Artist
from hmtc.models import Artist as ArtistModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")


def view_details(router, item):
    router.push(f"/artist-details/{item['id']}")


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router)

    parse_url_args()

    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Name", "value": "name", "width": "30%"},
        {"text": "URL", "value": "url"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [ArtistModel.name]

    with solara.Column(classes=["main-container"]):
        ArtistTable(
            router=router,
            headers=headers,
            base_query=ArtistModel.select(),
            search_fields=search_fields,
        )
