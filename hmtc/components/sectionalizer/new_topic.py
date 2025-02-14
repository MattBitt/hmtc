import solara


@solara.component_vue("./NewTopic.vue", vuetify=True)
def _NewTopic(event_create, event_reset):
    pass


@solara.component
def NewTopic(create, reset):
    _NewTopic(event_create=create, event_reset=reset)
