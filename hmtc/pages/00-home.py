import solara
import solara.lab

from hmtc.config import init_config

updating = solara.reactive(False)
config = init_config()


@solara.component
def Page():

    solara.Markdown("Home!")
