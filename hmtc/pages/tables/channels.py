from typing import Callable

import pandas as pd
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.channel_table import ChannelTable
from hmtc.models import Channel as ChannelModel

force_update_counter = solara.reactive(0)


@solara.component
def Page():
    base_query = ChannelModel.select()
    router = solara.use_router()
    MySidebar(router)

    headers = [
        {"text": "Title", "value": "title"},
        {"text": "Youtube ID", "value": "youtube_id"},
        {"text": "Last Update Completed", "value": "last_update_completed"},
        {"text": "Auto Update", "value": "auto_update"},
        {"text": "Files", "value": "files"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [ChannelModel.title, ChannelModel.url, ChannelModel.youtube_id]
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        ChannelTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
