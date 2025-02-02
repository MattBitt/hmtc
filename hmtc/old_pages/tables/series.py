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
        SeriesTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
