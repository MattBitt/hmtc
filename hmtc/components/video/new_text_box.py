from typing import Callable
import solara

from hmtc.schemas.video import VideoItem


@solara.component
def VideoNewTextBox(
    on_change: Callable[[str], None], on_new: Callable[[VideoItem], None]
):

    text_query = solara.use_reactive("")

    solara.InputText(
        "Search through Videos",
        value=text_query,
        continuous_update=True,
        on_value=on_change,
    )

    solara.Info(f"Current text_query = {text_query.value}")
