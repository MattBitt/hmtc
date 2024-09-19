from typing import Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel, Album as AlbumModel
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)
logger.debug("Albums Page Loaded")


@solara.component_vue("../components/album/album_table.vue", vuetify=True)
def AlbumTable(
    items: list = [],
    event_save_album=None,
    event_delete_album: Callable = None,
):
    pass


def delete_album(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    album = AlbumModel.get_by_id(item["id"])
    album.delete_instance()


def save_album(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        album = AlbumModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Album ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        AlbumModel.create(**edited_item)
        return
    vid = VideoModel.get_or_none(id=edited_item["video_id"])
    if vid is None:
        logger.error("Video Not Found. Cannot save Album")
        return

    album.title = edited_item["title"]
    album.release_date = edited_item["release_date"]
    album.video_id = edited_item["video_id"]
    album.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = (
        AlbumModel.select(AlbumModel)
        .join(VideoModel)
        .distinct()
        .order_by(AlbumModel.id.asc())
    )
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        AlbumTable(
            items=items,
            event_save_album=save_album,
            event_delete_album=delete_album,
        )
