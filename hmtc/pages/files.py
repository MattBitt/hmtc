from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.file_table import FileTable


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = FileModel.select(FileModel).order_by(FileModel.id.asc())
    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Filename", "value": "filename"},
        {"text": "Album ID", "value": "album_id"},
        {"text": "Track ID", "value": "track_id"},
        {"text": "Video ID", "value": "video_id"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [FileModel.filename]
    with solara.Column(classes=["main-container"]):
        FileTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
