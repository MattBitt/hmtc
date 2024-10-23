from typing import Optional, cast
import solara
from solara.alias import rv
import dataclasses
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from typing import Dict


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
