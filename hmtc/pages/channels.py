from typing import Callable

import pandas as pd
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.channel_table import ChannelTable
from hmtc.models import Channel as ChannelModel

force_update_counter = solara.reactive(0)


def delete_channel(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_channel(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        channel = ChannelModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Channel ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        ChannelModel.create(**edited_item)
        return

    channel.name = edited_item["name"]
    channel.url = edited_item["url"]
    channel.youtube_id = edited_item["youtube_id"]
    channel.enabled = edited_item["enabled"]
    channel.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    base_query = ChannelModel.select()
    router = solara.use_router()
    MySidebar(router)

    headers = [
        {"text": "Name", "value": "name"},
        {"text": "URL", "value": "url"},
        {"text": "Youtube ID", "value": "youtube_id"},
        {"text": "Enabled", "value": "enabled"},
        {"text": "Last Update Completed", "value": "last_update_completed"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [ChannelModel.name, ChannelModel.url, ChannelModel.youtube_id]
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        ChannelTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
