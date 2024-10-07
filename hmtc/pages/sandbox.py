import asyncio
import time

import ipyvue
import numpy as np
import solara
from loguru import logger
from peewee import fn
from solara.lab import Task, use_task

from hmtc.components.sandbox_component.sandbox import FancyComponent
from hmtc.components.shared.sidebar import MySidebar


def import_vue_components():
    ipyvue.register_component_from_file(
        "MyToolTipChip",
        "/home/matt/programming/hmtc/hmtc/components/my_tooltip_chip.vue",
        __file__,
    )


@solara.component_vue("sandbox.vue")
def Sandbox():
    pass


@solara.component
def Page():
    import_vue_components()
    MySidebar(router=solara.use_router())

    Sandbox()


@solara.component
def LiveUpdatingComponent(counter):
    """Component which will be redrawn whenever the counter value changes."""
    solara.Markdown(f"## Counter: {counter.value}")
