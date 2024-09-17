import pandas as pd
from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Track
from loguru import logger

force_update_counter = solara.reactive(0)
logger.debug("Tracks Page Loaded")


@solara.component_vue("../components/track/track_table.vue", vuetify=True)
def TrackTable(
    items: list = [],
    event_save_track=None,
    event_delete_track: Callable = None,
):
    pass


def delete_track(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    track = Track.get_by_id(item["id"])
    track.delete_instance()


def save_track(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        track = Track.get_by_id(item["id"])
    except Exception as e:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Track ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        Track.create(**edited_item)
        return

    track.title = edited_item["title"]
    track.track_number = edited_item["track_number"]
    track.album_id = edited_item["album_id"]
    track.video_id = edited_item["video_id"]
    track.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = Track.select()
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        TrackTable(
            items=items,
            event_save_track=save_track,
            event_delete_track=delete_track,
        )
