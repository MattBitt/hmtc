import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.video.no_sections_panel import NoSectionsPanel
from hmtc.components.video.section_details_panel import SectionsDetailsPanel
from hmtc.components.video.top_row import TopRow
from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.components.vue_registry import register_vue_components
from hmtc.domains.video import Video


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
    try:
        video = Video(video_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        router.push("/")
        return
    sections = []

    with solara.Column(classes=["main-container"]):

        VideoInfoPanel(video=video.instance)
        solara.Button(
            f"Edit Sections ({len(sections)})",
            on_click=lambda: router.push(
                f"/domains/section-details/{video.instance.id}"
            ),
            classes=["button"],
        )
        solara.Markdown(f"## Files")
        for file in video.file_repo.my_files(video.instance.id):
            solara.Markdown(f"### {file['file']}")
