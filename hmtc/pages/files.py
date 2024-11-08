from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import File as FileModel
from hmtc.schemas.file import File as FileItem

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/file/file_table.vue", vuetify=True)
def FileTable(
    items: list = [],
    event_save_file=None,
    event_delete_file: Callable = None,
):
    pass


def delete_file(item):
    logger.error(f"Not Implmeented!")
    return
    logger.debug(f"Deleting Item received from Vue: {item}")
    file = FileModel.get_by_id(item["id"])
    file.delete_instance()


def save_file(dict_of_items):
    logger.error(f"Not Implmeented!")
    return
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        file = FileModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"File ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        FileModel.create(**edited_item)
        return

    file.text = edited_item["text"]

    file.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = FileModel.select(FileModel).order_by(FileModel.id.asc())

    items = [
        FileItem.from_model(item).serialize()
        for item in base_query.order_by(FileModel.id.asc())
    ]
    with solara.Column(classes=["main-container"]):
        FileTable(
            items=items,
            event_save_file=save_file,
            event_delete_file=delete_file,
        )
