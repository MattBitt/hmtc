import solara
import solara.lab
from archive.sol import sidebar, main_content
from hmtc.components.app_bar import AppBar
from hmtc.pages import app_state


@solara.component
def Page():

    AppBar()
    with solara.Column():
        solara.Markdown("## Series")
