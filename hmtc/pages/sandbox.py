import dataclasses
import re
from typing import Dict, Optional, cast

import solara
from loguru import logger
from solara.alias import rv

from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.schemas.track import TrackItem
from hmtc.utils.jellyfin_functions import get_user_favorites


@solara.component_vue("sandbox.vue", vuetify=True)
def Sandbox(lyrics, currentTimestamp, event_update):
    pass


def parse_lrc_line(line):
    match = re.match(r"\[(\d+):(\d+):(\d+\.\d+)\](.*)", line)
    if match:
        hours, minutes, seconds, text = match.groups()
        timestamp = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return {"text": text.strip(), "timestamp": timestamp}
    return None


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    # track = TrackModel.get_or_none(TrackModel.id == 823)
    # track_item = TrackItem.from_model(track)

    with open("hmtc/pages/1 - boayncy, implosion, solar system.lrc", "r") as f:
        lyrics = f.readlines()
        raw_text = [line.strip() for line in lyrics]

        lyrics = [parse_lrc_line(line) for line in raw_text if parse_lrc_line(line)]

    timestamp = solara.use_reactive(0)

    def update_timestamp(*args):
        logger.error(f"update_timestamp {timestamp.value}")
        timestamp.set(timestamp.value + 1)

    Sandbox(
        lyrics=lyrics, currentTimestamp=timestamp.value, event_update=update_timestamp
    )
