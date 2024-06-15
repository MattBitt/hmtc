from typing import Callable

import plotly.graph_objects as go
import solara


def CompletionGauge(on_click: Callable[[dict], None], on_hover: Callable[[dict], None]):
    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=0.5,
            title={"text": "Tracks Created"},
        )
    )
    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)
