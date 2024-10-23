from typing import Optional, cast
import solara
from solara.alias import rv
import dataclasses

from hmtc.components.shared.sidebar import MySidebar
from typing import Dict
from hmtc.store import store_in_session_storage, read_from_session_storage


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    start_time = solara.use_reactive(read_from_session_storage("start_time"))
    solara.Markdown(f"Session started at {start_time.value}")
