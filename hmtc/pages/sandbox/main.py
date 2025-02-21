import solara
import solara.lab
from loguru import logger

from hmtc.components.shared import Chip, InputAndDisplay, MySpinner


@solara.component
def Sandbox():
    solara.Markdown(f"Sandbox Page.")
