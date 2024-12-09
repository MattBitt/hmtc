from pathlib import Path
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.track_table import TrackTable
from hmtc.domains.track import Track as TrackItem
from hmtc.models import Album as AlbumModel
from hmtc.models import Track as TrackModel

force_update_counter = solara.reactive(0)


from hmtc.router import parse_url_args


def delete_track(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


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

    parse_url_args()
    base_query = TrackModel.select()
    headers = [
        {"text": "Title", "value": "title"},
        {"text": "Track Number", "value": "track_number"},
        {"text": "Album", "value": "album.title", "sortable": False},
        {"text": "Section", "value": "section", "sortable": False},
        {"text": "Length", "value": "length"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [TrackModel.title]
    with solara.Column(classes=["main-container"]):
        TrackTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
