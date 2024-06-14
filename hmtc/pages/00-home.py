import solara
import solara.lab
import numpy as np
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
from hmtc.components.stats.percent_downloaded_gauge import PercentDownloadedGauge
from hmtc.mods.file import File
from hmtc.schemas.video import VideoItem

config = init_config()


@solara.component_vue("../components/shared/logo.vue")
def Logo():
    pass


def SubLogo(text):
    with solara.Row(classes=["sub-logo"]):
        solara.Text(text)


def tempPercentDownloadedGauge(current, total, on_click, on_hover):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=current,
            delta={"reference": total},
            gauge={"axis": {"visible": False}},
            domain={"row": 0, "column": 0},
        )
    )

    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)


def tempPercentDownloadedGauge2(stats, on_click, on_hover):
    logger.debug(f"About to create tempPercentDownloadedGauge2")

    fig = go.Figure()
    for s in stats:
        logger.debug(
            f"Stat: {s['name']} - downloaded = {s['downloaded']}  total={s['total']}"
        )

        fig.add_trace(
            go.Bar(
                y=[s["name"]],
                x=[s["downloaded"] / s["total"]] if s["total"] > 0 else [0],
                orientation="h",
            )
        )

    fig.update_layout(
        hoverlabel=dict(bgcolor="white", font_size=18, font_family="Rockwell"),
        yaxis=dict(title="Series"),
        xaxis=dict(title="Percent Downloaded"),
        title="Percent Downloaded by Series",
    )
    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)


def prepare_stats(stats):
    logger.debug(f"Preparing stats")
    logger.debug(f"Stats: {stats}")
    return stats


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )

    def on_click(*args):
        logger.info(f"click {args}")

    def on_hover(*args):
        # logger.info("hover")
        pass

    with solara.Column(classes=["main-container"]):
        with solara.Column(align="center"):
            current_downloaded = 50
            total_downloaded = 100
            stats = VideoItem.get_downloaded_stats_by_series()

            Logo()
            SubLogo(text=f"all harry mack")
            SubLogo(text=f"all the time...")
            with solara.Columns():
                # CompletionGauge(on_click=on_click, on_hover=on_hover)
                # tempPercentDownloadedGauge(
                #     current=50,
                #     total=100,
                #     on_click=on_click,
                #     on_hover=on_hover,
                # )
                tempPercentDownloadedGauge2(
                    stats=stats,
                    on_click=on_click,
                    on_hover=on_hover,
                )
