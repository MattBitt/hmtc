import solara
import solara.lab
from hmtc.components.my_app_bar import MyAppBar
from hmtc.models import Video


@solara.component
def Page():
    MyAppBar()
    with solara.Column():
        solara.Markdown("**About HMTC**")
        solara.Markdown("Coming soonish...")
