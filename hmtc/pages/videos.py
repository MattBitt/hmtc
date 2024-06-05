import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.shared.stats_display import StatsDisplay
from hmtc.components.video.cards_list import VideoCards
from hmtc.components.video.new_text_box import VideoSearchBox
from hmtc.states.videos_state import VideosState as State
from hmtc.components.app_bar import AppBar
from hmtc.components.shared.sidebar import MySidebar


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(
        router=router,
    )
    with solara.Card():

        # searchable text box
        VideoSearchBox(on_change=State.on_change_text_search, on_new=State.on_new)

        if State.videos.value:

            VideoCards(
                Ref(State.videos),
                router=router,
                on_save=State.on_save,
                on_update_from_youtube=State.on_update_from_youtube,
                on_delete=State.on_delete,
            )
        else:
            if State.text_query.value != "":
                solara.Error(
                    f"No videos found for {State.text_query.value}",
                    icon="mdi-alert-circle-outline",
                )
            else:
                solara.Button("Refresh", on_click=State.refresh_query)
                solara.Error("No videos found", icon="mdi-alert-circle-outline")
