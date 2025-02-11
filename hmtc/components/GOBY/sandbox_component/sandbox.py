import ipyvue
import solara


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
        "MyNextComponent", "ChildComponent2.vue", __file__
    )

    ipyvue.register_component_from_file(
        "ANewComponent", "ChildComponent3.vue", __file__
    )
    solara.Button(label="Hi")
    ParentComponent(myname="matt")
    ParentComponent(myname="lindsay")
    ParentComponent(iconName=Icons.USER.value)
