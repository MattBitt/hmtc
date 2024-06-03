import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.playlist.cards_list import PlaylistCards
from hmtc.components.playlist.new_text_box import PlaylistNewTextBox
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.shared.stats_display import StatsDisplay
from hmtc.states.playlists_state import PlaylistsState as State


@solara.component
def Page():

    with solara.Card():
        logger.debug("In Page and rendering Playlist list")
        logger.debug(f"Number of pages = {State.num_pages} found 🔵🔵🔵")

        with solara.Row():
            SortControls(State)
            PaginationControls(
                current_page=State.current_page,
                num_pages=State.num_pages,
                on_page_change=State.on_page_change,
            )

        # searchable text box
        PlaylistNewTextBox(on_change=State.on_change_text_search, on_new=State.on_new)

        if State.playlists.value:
            StatsDisplay(State.playlist_stats())
            PlaylistCards(
                Ref(State.playlists),
                on_update=State.on_update,
                on_delete=State.on_delete,
            )
        else:
            if State.text_query.value != "":
                solara.Error(
                    f"No playlists found for {State.text_query.value}",
                    icon="mdi-alert-circle-outline",
                )
            else:
                solara.Button("Refresh", on_click=State.refresh_query)
                solara.Error("No playlists found", icon="mdi-alert-circle-outline")
