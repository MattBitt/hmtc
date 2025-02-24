from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.tables.disc_table import DiscTable
from hmtc.models import Disc
from hmtc.models import Series as SeriesModel
from hmtc.models import Video as VideoModel
from hmtc.router import parse_url_args


@solara.component
def Page():
    base_query = Disc.select(Disc.id, Disc.title).order_by(Disc.title)
    router = solara.use_router()

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Album Title", "value": "album_title"},
        {"text": "Title", "value": "title"},
        {"text": "Folder", "value": "folder_name"},
        {"text": "Order", "value": "order"},
        {"text": "Num Videos", "value": "num_videos"},
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
