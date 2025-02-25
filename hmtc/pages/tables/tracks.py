from pathlib import Path
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger

from hmtc.components.tables.track_table import TrackTable
from hmtc.models import Album as AlbumModel
from hmtc.models import Track as TrackModel

force_update_counter = solara.reactive(0)


from hmtc.router import parse_url_args


@solara.component
def Page():

    router = solara.use_router()

    parse_url_args()
    base_query = TrackModel.select()
    headers = [
        {"text": "Title", "value": "title"},
        {"text": "Track Number", "value": "track_number"},
        {"text": "Album", "value": "album.title", "sortable": False},
        {"text": "Section", "value": "section_id", "sortable": False},
        {"text": "Length", "value": "length"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [TrackModel.title]
    with solara.Column(classes=["main-container"]):
        TrackTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
