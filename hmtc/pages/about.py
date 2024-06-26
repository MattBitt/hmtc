import solara

from hmtc.components.shared.sidebar import MySidebar


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(
        router=router,
    )
    with solara.Column(classes=["main-container"]):
        solara.Markdown("About Page!")
