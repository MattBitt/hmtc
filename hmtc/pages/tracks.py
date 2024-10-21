from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Album as AlbumModel
from hmtc.models import Track as TrackModel

force_update_counter = solara.reactive(0)


def create_query_from_url():
    # url options
    # /tracks should be a list of all tracks (default)
    # /tracks/album/<album_id> should be a list of tracks in an album

    all = TrackModel.select(
        TrackModel,
        AlbumModel,
    ).join(AlbumModel, peewee.JOIN.LEFT_OUTER)

    valid_filters = ["album"]
    router = solara.use_router()
    # level = solara.use_route_level()

    match router.parts:
        case [_, "all"]:
            # should probably show the unique column if all are shown
            return all, None, None, True
        case [_, filter, id_to_filter, "all"]:
            if filter in valid_filters:
                return (
                    all.where(getattr(TrackModel, filter) == id_to_filter),
                    filter,
                    id_to_filter,
                    True,
                )
            else:
                logger.debug(f"Invalid filter: {filter}")
                return None, None, None, False
        case [_, filter, id_to_filter]:
            if filter in valid_filters:
                return (
                    all.where(getattr(TrackModel, filter) == id_to_filter),
                    filter,
                    id_to_filter,
                    False,
                )
            else:
                logger.debug(f"Invalid filter: {filter}")
                return None, None, None, False
        case [_]:
            # this is the /tracks page view
            return all, None, None, False
        case _:
            logger.error(f"Invalid URL: {router.parts}")
            raise ValueError("Invalid URL")


@solara.component_vue("../components/track/track_table.vue", vuetify=True)
def TrackTable(
    items: list = [],
    event_save_track=None,
    event_delete_track: Callable = None,
):
    pass


def delete_track(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    track = TrackModel.get_by_id(item["id"])
    track.delete_instance()


def save_track(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        track = TrackModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Track ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        TrackModel.create(**edited_item)
        return

    track.title = edited_item["title"]
    track.track_number = edited_item["track_number"]
    track.album_id = edited_item["album_id"]
    track.video_id = edited_item["video_id"]
    track.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router)
    base_query, filter, id_to_filter, show_nonunique = create_query_from_url()
    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        TrackTable(
            items=items,
            event_save_track=save_track,
            event_delete_track=delete_track,
        )
