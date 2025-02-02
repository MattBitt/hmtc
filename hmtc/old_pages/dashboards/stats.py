from functools import reduce

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(
        router=router,
    )
    solara.Markdown("Stats Page")
