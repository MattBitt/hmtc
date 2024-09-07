from typing import cast


import solara
from hmtc.components.shared.sidebar import MySidebar


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        solara.Markdown("Sandbox")
