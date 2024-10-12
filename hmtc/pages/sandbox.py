import asyncio
import time
from typing import Callable

import ipyvue
import numpy as np
import solara
from loguru import logger
from peewee import fn
from solara.lab import Task, use_task

from hmtc.components.sandbox_component.sandbox import FancyComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopics as SectionTopicsModel


def import_vue_components():
    ipyvue.register_component_from_file(
        "SectionTimePanel", "../components/section/time_panel.vue", __file__
    )

    ipyvue.register_component_from_file(
        "BeatsInfo", "../components/beat/beats_info.vue", __file__
    )
    ipyvue.register_component_from_file(
        "ArtistsInfo", "../components/artist/artists_info.vue", __file__
    )

    ipyvue.register_component_from_file(
        "SectionAdminPanel", "../components/section/admin_panel.vue", __file__
    )

    ipyvue.register_component_from_file(
        "SectionTopicsPanel", "../components/section/topics_panel.vue", __file__
    )

    ipyvue.register_component_from_file(
        "SectionTimePanel", "../components/section/time_panel.vue", __file__
    )


@solara.component_vue("../components/shared/MySpinner.vue")
def Sandbox(section, topics):
    pass


@solara.component_vue("../components/shared/local_storage.vue")
def LocalStorage(
    key: str, value: str, on_value: Callable[[str], None] = None, debug: bool = False
): ...


counter = solara.reactive(0)


def set_initial_value(value: str):
    counter.value = int(value)


def increment():
    counter.value += 1


@solara.component
def Page():
    import_vue_components()
    MySidebar(router=solara.use_router())
    sect = (
        SectionModel.select(SectionModel.id, SectionModel.start, SectionModel.end)
        .order_by(fn.Random())
        .get()
        .model_to_dict()
    )
    topics = SectionTopicsModel.select(SectionTopicsModel.topic_id).where(
        SectionTopicsModel.section_id == sect["id"]
    )
    topic_dicts = [t.topic.model_to_dict() for t in topics]

    Sandbox(section=sect, topics=topic_dicts)
    LocalStorage(
        key="my-counter",
        value=str(counter.value),
        on_value=set_initial_value,
        debug=True,
    )
    solara.Button(f"Clicks: {counter.value}", on_click=increment)
    solara.Markdown(
        "Refresh the embedded page to see that we remember the counter value"
    )
