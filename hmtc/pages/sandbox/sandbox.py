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
from hmtc.utils.jellyfin_functions import can_ping_server, get_user_libraries, get_user_id, search_for_media, load_media_item, jf_seek_to, jf_playpause

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

    def load_item():
        res = search_for_media('videos', 'mgYKadMOwho')
        load_media_item(res['Id'])

    def seek():
        jf_seek_to(1000)
        
    def play():
        jf_playpause()

    with solara.Column(classes=["main-container"]):

        video = Video.get_by(id=1)
        with solara.Card():
            JFPanel(video)
        
        with solara.Card():
            
            user_id = get_user_id('user1')
            logger.debug(f"jf user id: {user_id}")
            logger.debug(get_user_libraries())
            solara.Button(f"Load Item", on_click=load_item, classes="button")
            solara.Button(f"Seek", on_click=seek, classes="button")
            solara.Button(f"Play", on_click=play, classes="button")

        
        

