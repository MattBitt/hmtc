from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.disc_table import DiscTable
from hmtc.models import Disc
from hmtc.models import Series as SeriesModel
from hmtc.models import Video as VideoModel
from hmtc.router import parse_url_args


@solara.component
def Page():
    base_query = Disc.select(Disc.id, Disc.title).order_by(Disc.title)
    router = solara.use_router()
    MySidebar(router)

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Title", "value": "title"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [Disc.title]
    with solara.Column(classes=["main-container"]):
        DiscTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
