import json
import urllib
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import solara


def CompletionGauge(on_click: Callable[[dict], None], on_hover: Callable[[dict], None]):
    def handle_hover(*args):
        pass

    def handle_click(*args):
        pass

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=56,
            max=100,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Analyzed"},
        )
    )

    return solara.FigurePlotly(fig, on_click=handle_click, on_hover=handle_hover)
