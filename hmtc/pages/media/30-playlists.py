import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.playlist.cards_list import PlaylistCards
from hmtc.components.playlist.new_text_box import PlaylistNewTextBox
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.shared.stats_display import StatsDisplay
from hmtc.states.playlists_state import PlaylistsState as State
from hmtc.components.app_bar import AppBar


@solara.component
def StatsDisplay(stats):

    # with solara.Row():
    #     solara.Text(f"Unique Content: ({stats['unique']})")

    solara.Markdown(f"#### Total: **({stats['total']})**")
    solara.Markdown(f"#### Enabled: **({stats['enabled']})**")


@solara.component
def Sidebar():
    with solara.Sidebar():
        solara.Markdown("Sidebar")
        with solara.Column():
            solara.Button("Videos", href="/media/videos")
            solara.Button("Playlists", href="/playlists")
            solara.Button("Settings", href="/settings")

            SortControls(State)
            PaginationControls(
                current_page=State.current_page,
                num_pages=State.num_pages,
                on_page_change=State.on_page_change,
            )
            StatsDisplay(State.stats())


@solara.component
def Page():
    Sidebar()
    with solara.Card():
        # searchable text box
        PlaylistNewTextBox(on_change=State.on_change_text_search, on_new=State.on_new)

        if State.playlists.value:

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
