from datetime import datetime
from typing import Any, Dict

import solara
import solara.lab
from loguru import logger

# program version
VERSION = "0.0.33"


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

    with solara.AppBar():
        solara.Button(
            icon_name="mdi-home", on_click=lambda: router.push("/"), icon=True
        )
        if True:  # logged_out
            solara.Button(
                icon_name="mdi-login", on_click=lambda: router.push("/login"), icon=True
            )
        else:
            solara.Button(
                icon_name="mdi-logout",
                on_click=lambda: router.push("/logout"),
                icon=True,
            )

        solara.Text(f"{VERSION}", classes=["version-number"])
        # solara.lab.ThemeToggle(enable_auto=False)
        with solara.Sidebar():
            # solara.InputText(label="global", value=app_state.value["value"])
            _Sidebar(
                version=VERSION,
                router=router,
                event_sidebar_clicked=sidebar_clicked,
            )
