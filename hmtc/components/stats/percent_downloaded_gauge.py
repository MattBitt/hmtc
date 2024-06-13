import json
import urllib
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import solara


def PercentDownloadedGauge(
    on_click: Callable[[dict], None], on_hover: Callable[[dict], None]
):

    fig = None

    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)
