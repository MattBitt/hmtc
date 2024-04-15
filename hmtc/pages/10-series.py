import solara
import solara.lab
from archive.sol import sidebar, main_content
from hmtc.components.my_app_bar import MyAppBar
from hmtc.pages import app_state


@solara.component
def Page():

    MyAppBar()
    with solara.Column():
        solara.Markdown("## Series")
