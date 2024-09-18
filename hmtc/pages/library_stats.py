import json
import urllib
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Playlist, Series, Video as VideoModel

title = "Library Stats"


def format_string(x: int):
    if x == 0:
        return "00:00:00"
    h, m, s = x // 3600, (x % 3600) // 60, x % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def SankeyPlot(df: pd.DataFrame):
    url = "https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    # override gray link colors with 'source' colors
    opacity = 0.4
    # change 'magenta' to its 'rgba' value to add opacity
    data["data"][0]["node"]["color"] = [
        "rgba(255,0,255, 0.8)" if color == "magenta" else color
        for color in data["data"][0]["node"]["color"]
    ]
    data["data"][0]["link"]["color"] = [
        data["data"][0]["node"]["color"][src].replace("0.8", str(opacity))
        for src in data["data"][0]["link"]["source"]
    ]

    fig = go.Figure(
        data=[
            go.Sankey(
                valueformat=".0f",
                valuesuffix="TWh",
                # Define nodes
                node=dict(
                    pad=15,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=data["data"][0]["node"]["label"],
                    color=data["data"][0]["node"]["color"],
                ),
                # Add links
                link=dict(
                    source=data["data"][0]["link"]["source"],
                    target=data["data"][0]["link"]["target"],
                    value=data["data"][0]["link"]["value"],
                    label=data["data"][0]["link"]["label"],
                    color=data["data"][0]["link"]["color"],
                ),
            )
        ]
    )

    fig.update_layout(
        title_text="Energy forecast for 2050<br>Source: Department of Energy & Climate Change, Tom Counsell via <a href='https://bost.ocks.org/mike/sankey/'>Mike Bostock</a>",
        font_size=10,
    )
    return fig


def SeriesDurationGraph(series):
    fig = go.Figure()
    data = dict(
        titles=[s.name for s in series],
        durations=[(s.duration // 3600) for s in series],
    )
    fig.add_trace(
        go.Bar(
            x=data["titles"],
            y=data["durations"],
            hovertemplate="Duration: %{y:.0f}<extra></extra> hours",
            showlegend=False,
        )
    )

    fig.update_layout(
        hoverlabel_align="right",
        title="Hours of Content by Series",
    )
    return fig


def PlaylistDurationGraph(plists):
    fig = go.Figure()
    data = dict(
        titles=[p.title for p in plists],
        durations=[(p.duration // 3600) for p in plists],
    )
    fig.add_trace(
        go.Bar(
            x=data["titles"],
            y=data["durations"],
            hovertemplate="Duration: %{y:.0f}<extra></extra> hours",
            showlegend=False,
        )
    )

    fig.update_layout(
        hoverlabel_align="right",
        title="Hours of Content by Playlist",
    )
    return fig


@solara.component
def StatsGraphs(on_click: Callable[[dict], None]):
    def handle_hover(*args):
        # logger.error(f"Graph Component Hovered Over")
        # logger.debug(f"args: {args}")
        pass

    def handle_click(*args):
        logger.error(f"Graph Component Clicked args={args}")
        pindex = args[0]["points"]["point_indexes"][0]
        logger.debug(f"Point Index: {pindex}")

    # logger.error(f"Current Selection: {current_selection.value}")
    pd.DataFrame({1, 2, 3, 4, 5})
    # Create figures in Express
    plists = (
        Playlist.select(
            Playlist.title,
            fn.Sum(VideoModel.duration).alias("duration"),
        )
        .join(VideoModel)
        .where(
            (
                VideoModel.duration.is_null(False)
                & (VideoModel.contains_unique_content == True)
            )
        )
        .group_by(Playlist)
    )

    series = (
        Series.select(
            Series.name,
            fn.Sum(VideoModel.duration).alias("duration"),
        )
        .join(VideoModel)
        .where(
            (
                VideoModel.duration.is_null(False)
                & (VideoModel.contains_unique_content == True)
            )
        )
        .group_by(Series)
    )

    fig1 = PlaylistDurationGraph(plists)
    fig2 = SeriesDurationGraph(series)

    with solara.ColumnsResponsive(12):
        solara.FigurePlotly(fig1, on_click=handle_click, on_hover=handle_hover)
        solara.FigurePlotly(fig2, on_click=handle_click, on_hover=handle_hover)
        # solara.FigurePlotly(figure1, on_click=handle_click, on_hover=handle_hover)
        # solara.FigurePlotly(figure4, on_click=handle_click, on_hover=handle_hover)


class State:
    loading = solara.reactive(False)

    @staticmethod
    def on_new():
        pass

    @staticmethod
    def on_delete():
        pass

    @staticmethod
    def on_click_graph(*args):
        logger.debug(f"on_click called with data: {args}")


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    with solara.Column(classes=["main-container"]):
        if State.loading.value:
            solara.SpinnerSolara(size="500px")
        else:
            StatsGraphs(on_click=State.on_click_graph)
