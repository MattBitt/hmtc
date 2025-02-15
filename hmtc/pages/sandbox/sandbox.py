from pathlib import Path

import solara
from loguru import logger

from hmtc.components.sectionalizer import Sectionalizer, StartFrequency
from hmtc.components.shared.ok_cancel import OkCancel
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.utils.jellyfin_functions import can_ping_server

choosing = solara.reactive(False)


@solara.component
def Step1():
    with solara.Card(title="Step1"):
        solara.Text(f"asdfasdfasdf")


@solara.component
def Step2():
    with solara.Card(title="Step2"):
        solara.Text(f"asdfasdfasdf")


@solara.component
def Page():

    def toggle_choose():
        choosing.set(not choosing.value)

    with solara.Column(classes=["main-container"]):

        video = Video.get_by(id=1)
        JFPanel(video)
        solara.Markdown(f"{can_ping_server()}")
        with solara.Card():
            solara.Button(label=f"Choose", on_click=toggle_choose, classes=["button"])

            with SwapTransition(show_first=(choosing.value == True), name="fade"):
                Step1()
                Step2()
        with solara.Card():
            solara.Button(label=f"Choose", on_click=toggle_choose, classes=["button"])

            with SwapTransition(show_first=(choosing.value == True), name="slide-fade"):
                Step2()
                Step1()
