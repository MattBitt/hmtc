from datetime import datetime
from typing import Any, Dict

import solara
import solara.lab
from loguru import logger

from hmtc.utils.version_manager import get_version

# program version
VERSION = f"v{get_version()}"


@solara.component_vue("./sidebar.vue")
def _Sidebar(
    version,
    event_sidebar_clicked,
):
    pass


# some app state that outlives a single page
app_state = solara.reactive({"user": "admin", "password": "admin", "value": 0})


@solara.component
def MySidebar(
    router,
):
    def sidebar_clicked(item):
        # need to add a check to make sure the route is existing
        router.push(item)
        return

    # solara.lab.ThemeToggle(enable_auto=False)
    with solara.Sidebar():
        # solara.InputText(label="global", value=app_state.value["value"])
        _Sidebar(
            version=VERSION,
            router=router,
            event_sidebar_clicked=sidebar_clicked,
        )
