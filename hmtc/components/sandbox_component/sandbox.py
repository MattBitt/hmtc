import ipyvue
import solara

from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("ParentComponent.vue")
def ParentComponent(myname: str = "", iconName: str = ""):
    pass


@solara.component
def FancyComponent():
    # Don't use reactivity in Page for this registration to work,
    # move that to another component if necessary.
    ipyvue.register_component_from_file(
        "MyChildComponent", "ChildComponent.vue", __file__
    )
    ipyvue.register_component_from_file(
        "MyNextComponent", "../shared/temp_child_component.vue", __file__
    )
    solara.Button(label="Hi")
    ParentComponent(myname="matt")
    ParentComponent(myname="lindsay")
    ParentComponent(iconName="mdi-account")