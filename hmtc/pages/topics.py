from typing import Callable
import solara
from peewee import fn
import peewee
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Topic as TopicModel
import pandas as pd
from loguru import logger

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

    topic.text = edited_item["name"]
    topic.start_date = edited_item["start_date"]
    topic.end_date = edited_item["end_date"]

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

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        TopicTable(
            items=items,
            event_save_topic=save_topic,
            event_delete_video_item=delete_topic,
        )
