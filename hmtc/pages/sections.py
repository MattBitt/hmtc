from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.section_table import SectionTable
from hmtc.models import Section as SectionModel
from hmtc.schemas.section import Section as SectionItem

force_update_counter = solara.reactive(0)


def view_details(router, item):
    router.push(f"/video-details/{item['video_id']}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = SectionModel.select(SectionModel).order_by(SectionModel.id.asc())

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Start", "value": "start"},
        {"text": "End", "value": "end"},
        {"text": "Video ID", "value": "video_id"},
        {"text": "Type", "value": "section_type"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = []
    with solara.Column(classes=["main-container"]):
        SectionTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
