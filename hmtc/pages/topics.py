from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import SectionTopics as SectionTopicModel
from hmtc.models import Topic as TopicModel
from hmtc.schemas.topic import Topic as TopicItem

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/topic/topic_table.vue", vuetify=True)
def TopicTable(
    items: list = [],
    event_save_topic=None,
    event_delete_topic: Callable = None,
):
    pass


def delete_topic(item):
    logger.debug(f"Deleting Item received from Vue: {item}")
    topic = TopicModel.get_by_id(item["id"])
    topic.delete_instance()


def save_topic(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    logger.debug(f"Item received from Vue: {item}")

    try:
        topic = TopicModel.get_by_id(item["id"])
    except Exception:
        ## this should probably check item for id instead of edited_item
        logger.debug(f"Topic ID not found. Creating {edited_item}")
        edited_item["id"] = None  # db should assign id
        TopicModel.create(**edited_item)
        return

    topic.text = edited_item["text"]

    topic.save()
    force_update_counter.set(force_update_counter.value + 1)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)

    base_query = (
        TopicModel.select(
            TopicModel.id,
            TopicModel.text,
        )
        .group_by(TopicModel.id, TopicModel.text)
        .order_by(TopicModel.text.asc())
    )

    items = [TopicItem.from_model(item).serialize() for item in base_query]
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        TopicTable(
            items=items,
            event_save_topic=save_topic,
            event_delete_topic=delete_topic,
        )
