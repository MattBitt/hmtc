from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Series, Series, YoutubeSeries, Playlist
from hmtc.schemas.video import VideoItem
import peewee
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)


@solara.component_vue(
    "../components/youtube_series/youtube_series_table.vue", vuetify=True
)
def SeriesTable(
    items: list = [],
    event_save_youtube_series=None,
    event_delete_youtube_series: Callable = None,
    serieses: list = [],
    selected_series: dict = None,
):
    pass


def delete_youtube_series(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_youtube_series(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    selected_series = dict_of_items["selectedSeries"]
    logger.debug(f"Item received from Vue: {item}")
    series = None

    try:
        youtube_series = YoutubeSeries.get_by_id(item["id"])
    except Exception as e:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Series ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        YoutubeSeries.create(**edited_item)
        return

    if selected_series["id"] is not None:
        logger.debug(f"Selected series: {selected_series}")
        if selected_series["id"] != youtube_series.series.id:
            series = Series.get_by_id(selected_series["id"])

            logger.debug(
                f"Series id is different. Need to update to {series} from {youtube_series.series.name}"
            )

    youtube_series.title = edited_item["title"]
    if series is not None:
        youtube_series.series = series
    youtube_series.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = YoutubeSeries.select()
    router = solara.use_router()
    MySidebar(router)
    serieses = [
        {"id": series.id, "name": series.name}
        for series in Series.select().order_by(Series.name)
    ]
    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        SeriesTable(
            items=items,
            serieses=serieses,
            selected_series={"id": None, "name": None},
            event_save_youtube_series=save_youtube_series,
            event_delete_video_item=delete_youtube_series,
        )
