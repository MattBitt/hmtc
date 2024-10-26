import dataclasses
from typing import Dict, Optional, cast

import solara
from loguru import logger
from solara.alias import rv

from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.jellyfin_functions import get_user_favorites


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    PlotlyFigureComponent()
    favs = get_user_favorites()
    for fav in sorted(favs, key=lambda x: x["Name"]):
        solara.Markdown(f"## {fav['Name']}")
