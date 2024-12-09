from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.topic_table import TopicTable
from hmtc.domains.topic import Topic as TopicItem
from hmtc.models import SectionTopics as SectionTopicModel
from hmtc.models import Topic as TopicModel
from hmtc.router import parse_url_args

force_update_counter = solara.reactive(0)


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
    parse_url_args()
    base_query = (
        TopicModel.select(
            TopicModel.id,
            TopicModel.text,
        )
        .group_by(TopicModel.id, TopicModel.text)
        .order_by(TopicModel.text.asc())
        .limit(100)
    )

    headers = [
        {"text": "ID", "value": "id"},
        {"text": "Text", "value": "text"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]
    search_fields = [TopicModel.text]

    with solara.Column(classes=["main-container"]):
        TopicTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
