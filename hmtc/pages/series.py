from typing import Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Series
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/series/series_table.vue", vuetify=True)
def SeriesTable(
    items: list = [],
    event_save_series=None,
    event_delete_series: Callable = None,
):
    pass


def delete_series(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_series(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        series = Series.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Series ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        Series.create(**edited_item)
        return

    series.name = edited_item["name"]
    series.start_date = edited_item["start_date"]
    series.end_date = edited_item["end_date"]

    series.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = Series.select()
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        SeriesTable(
            items=items,
            event_save_series=save_series,
            event_delete_video_item=delete_series,
        )
