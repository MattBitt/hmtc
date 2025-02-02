import solara
import solara.lab
from loguru import logger




@solara.component
def Page():


    with solara.Column(classes=["main-container"]):
        solara.Markdown(f"## A Main page with a bunch of links")
        with solara.lab.Tabs(align="center"):
            solara.lab.Tab("asdf", path_or_route='/')