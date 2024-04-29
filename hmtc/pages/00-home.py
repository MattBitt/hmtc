import solara
import solara.lab
from solara.lab import task
from loguru import logger
import time
from hmtc.models import Video, VideoFile
from hmtc.config import init_config
from hmtc.components.my_app_bar import MyAppBar

updating = solara.reactive(False)


config = init_config()


@solara.component
def Page():
    MyAppBar(env=config.get("GENERAL", "ENVIRONMENT"))
    solara.Markdown("Home!")
