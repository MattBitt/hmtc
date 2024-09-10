from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Channel, Series, YoutubeSeries, Playlist
from hmtc.schemas.video import VideoItem
import peewee
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/channel/channel_table.vue", vuetify=True)
def ChannelTable(
    items: list = [],
    event_save_channel=None,
    event_delete_channel: Callable = None,
):
    pass


def delete_channel(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_channel(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        channel = Channel.get_by_id(item["id"])
    except Exception as e:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Channel ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        Channel.create(**edited_item)
        return

    channel.name = edited_item["name"]
    channel.url = edited_item["url"]
    channel.youtube_id = edited_item["youtube_id"]
    channel.enabled = edited_item["enabled"]
    channel.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = Channel.select()
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        ChannelTable(
            items=items,
            event_save_channel=save_channel,
            event_delete_video_item=delete_channel,
        )
