import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(
        router=router,
    )
    solara.Markdown("Settings")
