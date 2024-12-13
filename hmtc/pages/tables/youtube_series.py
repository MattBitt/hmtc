from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.youtube_series_table import YoutubeSeriesTable
from hmtc.models import Series as SeriesModel
from hmtc.models import Video as VideoModel
from hmtc.models import YoutubeSeries
from hmtc.router import parse_url_args


@solara.component
def Page():
    base_query = YoutubeSeries.select(
        YoutubeSeries.id, YoutubeSeries.title, YoutubeSeries.series_id
    ).order_by(YoutubeSeries.title)
    router = solara.use_router()
    MySidebar(router)
    args = parse_url_args()
    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Title", "value": "title"},
        {"text": "Series", "value": "series"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [YoutubeSeries.title]
    with solara.Column(classes=["main-container"]):
        YoutubeSeriesTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
