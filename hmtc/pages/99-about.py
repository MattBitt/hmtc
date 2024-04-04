import solara
import solara.lab
from hmtc.components.app_bar import AppBar
from hmtc.models import Video


@solara.component
def Page():
    AppBar()
    with solara.Column():
        solara.Markdown("**About HMTC**")
        solara.Markdown("Coming soonish...")
