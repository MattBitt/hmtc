import solara
import ipyvue
from loguru import logger
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.section import SectionManager
from hmtc.schemas.video import VideoItem


@solara.component_vue("../components/shared/carousel.vue")
def Carousel(
    sections: list = [],
):
    pass


@solara.component
def Page():
    video_id = 62
    video = VideoItem.get_details_for_video(video_id)

    sm = SectionManager.from_video(video)
    sects = [item.model_to_dict() for item in sm.sections]
    Carousel(sections=sects)
