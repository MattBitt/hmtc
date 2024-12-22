from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.topic_table import TopicTable

from hmtc.models import Topic as TopicModel
from hmtc.router import parse_url_args


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)
    parse_url_args()
    base_query = (
        TopicModel.select(
            TopicModel.id,
            TopicModel.text,
        )
        .group_by(TopicModel.id, TopicModel.text)
        .order_by(TopicModel.text.asc())
        .limit(100)
    )

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Text", "value": "text"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [TopicModel.text]

    with solara.Column(classes=["main-container"]):
        TopicTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
