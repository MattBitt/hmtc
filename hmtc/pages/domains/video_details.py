import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.video.no_sections_panel import NoSectionsPanel
from hmtc.components.video.section_details_panel import SectionsDetailsPanel
from hmtc.components.video.top_row import TopRow
from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.components.vue_registry import register_vue_components
from hmtc.domains.section import Section
from hmtc.domains.video import Video as VideoItem


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        router.push("/domains/videos")
    else:
        return router.parts[level:][0]
    logger.error(f"Does this execute? {router.parts}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    register_vue_components(file=__file__)

    video_id = parse_url_args()
    if video_id is None or video_id == 0:
        with solara.Error():
            solara.Markdown(f"No Video Found {video_id}")
        return

    video = VideoItem.load(video_id)
    sections = Section.load_for_video(video.id)
    reactive_sections = solara.use_reactive(sections)

    with solara.Column(classes=["main-container"]):
        TopRow(
            video=video,
            reactive_sections=reactive_sections,
        )

        VideoInfoPanel(video=video)

        if len(reactive_sections.value) == 0:
            NoSectionsPanel(
                video=video,
            )
        else:
            SectionsDetailsPanel(
                video=video,
                reactive_sections=reactive_sections,
            )
