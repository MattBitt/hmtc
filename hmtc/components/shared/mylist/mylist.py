import solara
from loguru import logger


@solara.component_vue("./ListVue.vue", vuetify=True)
def ListVue(title, items):
    pass


@solara.component
def MyList(title="MyList Default Title", items=[]):

    ListVue(title=title, items=items)
