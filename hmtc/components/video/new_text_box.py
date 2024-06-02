from typing import Callable

import solara

from hmtc.schemas.video import VideoItem


@solara.component
def CustomTextBox(
    label: str,
    value: solara.Reactive[VideoItem],
    on_new: Callable[[str], None] = None,
    on_value: Callable[[str], None] = None,
    continuous_update: bool = True,
    **kwargs,
):
    solara.InputText(
        label=label,
        value=value,
        on_value=on_value,
        continuous_update=continuous_update,
        **kwargs,
    )


@solara.component
def VideoSearchBox(
    on_change: Callable[[str], None], on_new: Callable[[VideoItem], None]
):

    text_query = solara.use_reactive("")

    CustomTextBox(
        label="Videos",
        value=text_query,
        on_value=on_change,
    )

    solara.Info(f"Current text_query = {text_query.value}")
