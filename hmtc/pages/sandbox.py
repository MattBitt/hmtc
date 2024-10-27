import dataclasses
import re
from typing import Dict, Optional, cast

import solara
from loguru import logger
from solara.alias import rv

from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.sidebar import MySidebar
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
    lyrics = [
        {"text": "Hello", "timestamp": 0},
        {"text": "World", "timestamp": 1},
        {"text": "!", "timestamp": 2},
        {"text": "Hello Again", "timestamp": 8},
    ]
    with open("hmtc/utils/output.lrc", "r") as f:
        lyrics = f.readlines()
        raw_text = [line.strip() for line in lyrics]

        lyrics = [parse_lrc_line(line) for line in raw_text if parse_lrc_line(line)]

    timestamp = solara.use_reactive(15 * 60)

    def update_timestamp(*args):
        logger.error(f"update_timestamp {timestamp.value}")
        timestamp.set(timestamp.value + 1)

    Sandbox(
        lyrics=lyrics, currentTimestamp=timestamp.value, event_update=update_timestamp
    )
