import solara


@solara.component_vue("check.vue", vuetify=True)
def _Check():
    pass


@solara.component_vue("x.vue", vuetify=True)
def _X():
    pass


@solara.component
def Check():
    return _Check()


@solara.component
def X():
    return _X()
