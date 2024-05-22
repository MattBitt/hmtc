import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.video.cards_list import VideoCards
from hmtc.components.video.new_text_box import VideoSearchBox
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.shared.stats_display import StatsDisplay
from hmtc.states.video_sections import VideoSectionsState as State


@solara.component
def VideoSectionsPage(video):
    solara.Success(f"Video Sections Page")
    solara.Success(f"Video = {video}")


@solara.component
def Page():

    router = solara.use_router()
    level = solara.use_route_level()
    video = solara.reactive(State.grab_video(router, level))
    if video is None:
        solara.Error(f"No video Found", icon="mdi-alert-circle-outline")
        return
    VideoSectionsPage(video)
