from pathlib import Path
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.track_table import TrackTable
from hmtc.models import Album as AlbumModel
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from archive.track import Track as TrackItem

force_update_counter = solara.reactive(0)


def create_query_from_url():
    # url options
    # /tracks should be a list of all tracks (default)
    # /tracks/album/<album_id> should be a list of tracks in an album
    # /tracks/missing-files/audio should be a list of tracks missing audio files
    # /tracks/missing-files/lyrics should be a list of tracks missing video files
    all = (
        TrackModel.select(
            TrackModel,
            AlbumModel,
        )
        .join(AlbumModel, peewee.JOIN.LEFT_OUTER)
        .switch(TrackModel)
    )

    router = solara.use_router()

    match router.parts:
        case ["tracks"]:
            return all, None, None
        case ["tracks", "album", album_id]:
            tracks = all.where(TrackModel.album_id == album_id)
            return tracks, "album", album_id
        case ["tracks", "missing-files", file_type]:
            if file_type not in ["audio", "lyrics"]:
                logger.error(f"Invalid file type: {file_type}")
                return
            tracks_with_files = (
                TrackModel.select(TrackModel)
                .join(FileModel, on=(TrackModel.id == FileModel.track_id))
                .where(FileModel.file_type == file_type)
            )
            all_tracks = TrackModel.select()
            tracks = all_tracks - tracks_with_files
            return tracks, "missing-files", file_type

        case _:
            logger.error(f"Invalid URL: {router.url}")


def delete_track(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    for file in item["files"]:
        file = FileModel.get_by_id(file["id"])
        file_path = Path(file.path) / file.filename
        file_path.unlink()
        file.delete_instance()
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
    base_query, filter, id_to_filter = create_query_from_url()
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
