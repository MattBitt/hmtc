import solara
import ipyvue
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("sandbox.vue")
def Sandbox():
    pass


@solara.component
def Page():

    MySidebar(router=solara.use_router())
    Sandbox()
