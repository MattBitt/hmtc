import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.tables.superchat_segment_table import SuperchatSegmentTable
from hmtc.models import SuperchatSegment as SuperchatSegmentModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")


def view_details(router, item):
    router.push(f"/superchat_segment-details/{item['id']}")


@solara.component
def Page():

    router = solara.use_router()

    parse_url_args()

    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Start", "value": "start_time_ms"},
        {"text": "End", "value": "end_time_ms"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [SuperchatSegmentModel.start_time_ms]

    with solara.Column(classes=["main-container"]):
        SuperchatSegmentTable(
            router=router,
            headers=headers,
            base_query=SuperchatSegmentModel.select(),
            search_fields=search_fields,
        )
