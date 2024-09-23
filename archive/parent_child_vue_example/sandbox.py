import solara
import ipyvue
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("ParentComponent.vue")
def ParentComponent(myname: str = ""):
    pass


@solara.component
def Page():
    # Don't use reactivity in Page for this registration to work,
    # move that to another component if necessary.
    MySidebar(router=solara.use_router())
    ipyvue.register_component_from_file(
        "MyChildComponent", "ChildComponent.vue", __file__
    )

    ParentComponent(myname="matt")
