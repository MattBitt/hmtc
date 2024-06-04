from typing import Callable

import solara

from hmtc.schemas.playlist import PlaylistItem


@solara.component
def PlaylistNewTextBox(
    on_change: Callable[[str], None], on_new: Callable[[PlaylistItem], None]
):

    text_query = solara.use_reactive("")

    solara.InputText(
        "Search through Playlists",
        value=text_query,
        continuous_update=True,
        on_value=on_change,
    )
