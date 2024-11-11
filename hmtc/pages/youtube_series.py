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

force_update_counter = solara.reactive(0)


def delete_youtube_series(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    youtube_series = YoutubeSeries.get_by_id(item["id"])
    youtube_series.delete_instance()


def remove_series_from_youtube_series(item):
    youtube_series = YoutubeSeries.get_by_id(item)
    youtube_series.series = None
    youtube_series.save()


def save_youtube_series(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    selected_series = dict_of_items["selectedSeries"]
    logger.debug(f"Item received from Vue: {item}")
    series = None

    try:
        youtube_series = YoutubeSeries.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"YoutubeSeries ID not found. Creating {edited_item}")
        youtube_series = YoutubeSeries.create(title=edited_item["title"])

    if selected_series["id"] is not None:
        series = SeriesModel.get_by_id(selected_series["id"])

    youtube_series.title = edited_item["title"]
    if series is not None:
        youtube_series.series = series
    youtube_series.save()


@solara.component
def Page():
    base_query = YoutubeSeries.select(
        YoutubeSeries.id, YoutubeSeries.title, YoutubeSeries.series_id
    ).order_by(YoutubeSeries.title)
    router = solara.use_router()
    MySidebar(router)
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
