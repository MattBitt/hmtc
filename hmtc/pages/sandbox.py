import time

import numpy as np


import solara
import numpy as np


import solara
import ipyvue
import solara
from loguru import logger
from peewee import fn
from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.models import Video as VideoModel
from hmtc.models import File as FileModel


import asyncio
import solara
from solara.lab import use_task, Task


@solara.component_vue("../components/shared/jellyfin_control_panel.vue")
def Sandbox(session_id):
    pass


live_update = solara.reactive(False)

""" 
Mediabrowser Token="d035af26e54542e9a3a31785ec260e14"
"""

"""
user1 id
f6f0fa8013a94ee3a1161bae8af59733
"""


@solara.component
def Page():

    MySidebar(router=solara.use_router())

    # number = solara.use_reactive(4)
    jf = MyJellyfinClient()

    # # define some state which will be updated regularly in a separate thread
    # counter = solara.use_reactive(0)
    # new_play_status_variable = solara.use_reactive("")
    # need_to_update_again = False

    # def render():
    #     """Infinite loop regularly mutating counter state"""
    #     update_timer = 0
    #     while True:
    #         time.sleep(1)
    #         if jf.is_connected:
    #             status = jf.get_playing_status_from_jellyfin()

    #             if status["status"] == "playing":
    #                 update_timer += 1
    #                 counter.value += 1

    #             if update_timer == 5:
    #                 update_timer = 0

    #                 if jf.is_connected:

    #                     if status is None:
    #                         logger.error("No active session found.")
    #                         return

    #                     postion = status["position"]
    #                     new_play_status_variable.value = status

    #                     counter.value = postion

    # result: Task[int] = use_task(render, dependencies=[counter.value])
    # # result: solara.Result[bool] = solara.use_thread(render)
    # if result.error:
    #     raise result.error

    # # create the LiveUpdatingComponent, this component depends on the counter
    # # value so will be redrawn whenever counter value changes
    # LiveUpdatingComponent(counter.value)

    Sandbox(session_id=jf.session_id)


@solara.component
def LiveUpdatingComponent(counter):
    """Component which will be redrawn whenever the counter value changes."""
    solara.Markdown(f"## Counter: {counter.value}")
