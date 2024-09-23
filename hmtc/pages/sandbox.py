import solara
import ipyvue
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.section import SectionManager
from hmtc.schemas.video import VideoItem


@solara.component_vue("ParentComponent.vue")
def ParentComponent(myname: str = ""):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionTimeLine(
    whole_start=0,
    whole_end=2447,
    part_start=600,
    part_end=1200,
    event_prev_slide: callable = None,
    event_next_slide: callable = None,
):
    pass


@solara.component
def Page():
    video_id = 285
    video = VideoItem.get_details_for_video(video_id)
    model = solara.use_reactive(0)
    sm = SectionManager.from_video(video)

    SectionTimeLine(
        whole_start=0,
        whole_end=video.duration,
        part_start=sm.sections[model.value].start // 1000,
        part_end=sm.sections[model.value].end // 1000,
        event_prev_slide=lambda: logger.debug("prev"),
        event_next_slide=lambda: logger.debug("next"),
    )
