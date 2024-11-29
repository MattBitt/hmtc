import solara
from loguru import logger


@solara.component_vue("check.vue", vuetify=True)
def _Check(
    clickable=False,
    event_click=lambda: logger.info("Check clicked Default"),
    icon_color="success",
):
    pass


@solara.component_vue("x.vue", vuetify=True)
def _X(
    clickable=False,
    event_click=lambda: logger.info("Check clicked Default"),
    icon_color="error",
):
    pass


@solara.component
def Check(icon_color="success"):
    return _Check(icon_color=icon_color)


@solara.component
def CheckClickable(on_click, icon_color="success"):
    return _Check(clickable=True, event_click=on_click, icon_color=icon_color)


@solara.component
def X(icon_color="error"):
    return _X(icon_color=icon_color)


@solara.component
def XClickable(on_click, icon_color="error"):
    return _X(clickable=True, event_click=on_click, icon_color=icon_color)
