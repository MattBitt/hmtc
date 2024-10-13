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

    ipyvue.register_component_from_file(
        "AutoComplete",
        "../components/shared/AutoComplete.vue",
        __file__,
    )


@solara.component_vue("../components/video/AlbumPanel.vue")
def Sandbox(event_create_album):
    pass


@solara.component
def Page():
    import_vue_components()
    MySidebar(router=solara.use_router())

    Sandbox(
        event_create_album=lambda x: logger.info(
            f"Event create album received in python! args = {x}"
        )
    )
