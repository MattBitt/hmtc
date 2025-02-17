import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.tables.superchat_table import SuperchatTable
from hmtc.models import Superchat as SuperchatModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")


def view_details(router, item):
    router.push(f"/superchat-details/{item['id']}")


@solara.component
def Page():

    router = solara.use_router()

    parse_url_args()

    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Frame", "value": "frame", "width": "30%"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [SuperchatModel.frame]

    with solara.Column(classes=["main-container"]):
        SuperchatTable(
            router=router,
            headers=headers,
            base_query=SuperchatModel.select(),
            search_fields=search_fields,
        )
