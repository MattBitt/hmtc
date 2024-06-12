import solara
import solara.lab
from loguru import logger
import json
import urllib
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.components.completion_gauge import CompletionGauge
from hmtc.mods.file import File

config = init_config()


@solara.component_vue("../components/shared/logo.vue")
def Logo():
    pass


def SubLogo(text):
    with solara.Row(classes=["sub-logo"]):
        solara.Text(text)


def CompletionGauge(on_click: Callable[[dict], None], on_hover: Callable[[dict], None]):
    def handle_hover(*args):
        pass

    def handle_click(*args):
        pass

    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=0.5,
            title={"text": "Tracks Created"},
        )
    )
    return solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )

    def on_click(*args):
        logger.info("click")

    def on_hover(*args):
        logger.info("hover")

    with solara.Column(classes=["main-container"]):
        with solara.Column(align="center"):
            Logo()
            SubLogo(text=f"all harry mack")
            SubLogo(text=f"all the time...")
            CompletionGauge(on_click=on_click, on_hover=on_hover)
