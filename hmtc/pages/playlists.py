from typing import Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Playlist
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/playlist/playlist_table.vue", vuetify=True)
def PlaylistTable(
    items: list = [],
    event_save_playlist=None,
    event_delete_playlist: Callable = None,
):
    pass


def delete_playlist(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_playlist(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        playlist = Playlist.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Playlist ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        Playlist.create(**edited_item)
        return

    playlist.title = edited_item["title"]
    playlist.url = edited_item["url"]
    playlist.youtube_id = edited_item["youtube_id"]
    playlist.enabled = edited_item["enabled"]
    playlist.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = Playlist.select()
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        PlaylistTable(
            items=items,
            event_save_playlist=save_playlist,
            event_delete_video_item=delete_playlist,
        )
