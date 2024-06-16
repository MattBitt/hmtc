import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("./sandbox.vue")
def Sandbox(playbackTime=0):
    pass


@solara.component_vue("../components/shared/logo.vue")
def Logo():
    pass


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Sandbox")

        # use this to test out new vue components
        # just change the contents of the vue file and refresh the page
        Sandbox(event_trigger=lambda data: logger.error("asdf"))
        # f = File.from_path("1/asdf.txt")
        # f.move_to("new_folder")
