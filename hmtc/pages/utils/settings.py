import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.importer.existing_files import import_sections


@solara.component
def SectionsControls():
    with solara.Columns():
        with solara.Card("Videos"):
            with solara.Column():
                solara.Text(f"Import Videos")
                solara.Button("Scan Local", on_click=None, classes=["button"])
        with solara.Card("Sections"):
            with solara.Column():
                solara.Text(f"Import Sections")
                solara.Button("Start", on_click=import_sections, classes=["button"])


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown(f"# Settings Page")
    SectionsControls()
