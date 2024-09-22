import solara
import ipyvue
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("ParentComponent.vue")
def ParentComponent(myname: str = ""):
    pass


@solara.component_vue("../components/file/file_type_checkboxes.vue", vuetify=True)
def FileTypeCheckboxes(
    has_audio: bool = False,
    has_video: bool = False,
    has_subtitle: bool = False,
    has_info: bool = True,
    has_poster: bool = True,
    event_download_video: callable = None,
    event_download_info: callable = None,
):
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
    FileTypeCheckboxes()
