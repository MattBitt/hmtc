from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Section as SectionModel
from hmtc.schemas.section import Section as SectionItem

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/section/section_table.vue", vuetify=True)
def SectionTable(
    items: list = [],
    event_save_section=None,
    event_delete_section: Callable = None,
    event_link1_clicked: Callable = None,
):
    pass


def delete_section(item):
    logger.error(f"Not Implmeented!")
    return
    logger.debug(f"Deleting Item received from Vue: {item}")
    section = SectionModel.get_by_id(item["id"])
    section.delete_instance()


def save_section(dict_of_items):
    logger.error(f"Not Implmeented!")
    return
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        section = SectionModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Section ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        SectionModel.create(**edited_item)
        return

    section.text = edited_item["text"]

    section.save()
    force_update_counter.set(force_update_counter.value + 1)


def view_details(router, item):
    router.push(f"/video-details/{item['video_id']}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = SectionModel.select(SectionModel).order_by(SectionModel.id.asc())

    items = [SectionItem.from_model(item).serialize() for item in base_query]
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        SectionTable(
            items=items,
            event_save_section=save_section,
            event_delete_section=delete_section,
            event_link1_clicked=lambda x: view_details(router, x),
        )
