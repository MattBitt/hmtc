import dataclasses
import re
from pathlib import Path
from typing import Dict, Optional, cast

import solara
from loguru import logger
from solara.alias import rv

from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.schemas.track import TrackItem
from hmtc.utils.jellyfin_functions import get_current_user_timestamp


@solara.component_vue("sandbox.vue", vuetify=True)
def Sandbox(inviteList=["matthew", "mark", "luke", "john"]):
    pass


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    Sandbox()
