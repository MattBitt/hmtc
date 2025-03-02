import solara
from loguru import logger


@solara.component_vue("./Chip.vue", vuetify=True)
def ChipVue(item, color, closable, event_close):
    pass


@solara.component
def Chip(item, color="primary", event_close=None):
    closable = event_close is not None

    ChipVue(item=item, color=color, closable=closable, event_close=event_close)
