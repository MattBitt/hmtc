from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.series_table import SeriesTable
from hmtc.domains.series import Series as SeriesItem
from hmtc.models import Series as SeriesModel

force_update_counter = solara.reactive(0)


def delete_series(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    series = SeriesModel.get_by_id(item["id"])
    series.delete_instance()


def save_series(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        series = SeriesModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Series ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        SeriesModel.create(**edited_item)
        return

    series.title = edited_item["title"]
    series.start_date = edited_item["start_date"]
    series.end_date = edited_item["end_date"]

    series.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = SeriesModel.select()

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Title", "value": "title"},
        {"text": "Start Date", "value": "start_date"},
        {"text": "End Date", "value": "end_date"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [SeriesModel.title]
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        SeriesTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
