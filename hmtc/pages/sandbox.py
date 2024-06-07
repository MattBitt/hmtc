import solara

from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("./sandbox.vue")
def Sandbox():
    pass


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    solara.Markdown("## Sandbox")

    # use this to test out new vue components
    # just change the contents of the vue file and refresh the page
    Sandbox()
