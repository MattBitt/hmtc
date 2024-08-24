import solara
import solara.lab

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config

config = init_config()


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )

    with solara.Column(classes=["main-container"]):
        with solara.Column(align="center"):
            solara.Markdown("Home")
