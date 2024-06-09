import solara
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from solara.lab.toestand import Ref


@solara.component_vue("./sandbox.vue")
def Sandbox(event_trigger2):
    pass


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    solara.Markdown("## Sandbox")

    # use this to test out new vue components
    # just change the contents of the vue file and refresh the page
    Sandbox(event_trigger=lambda data: logger.error("triggggggggered"))
