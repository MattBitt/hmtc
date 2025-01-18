from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.video.no_sections_panel import NoSectionsPanel
from hmtc.components.video.section_details_panel import SectionsDetailsPanel
from hmtc.components.video.top_row import TopRow
from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.domains.video import Video
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = config["WORKING"]


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

    def download_video():
        results = download_video_file(
            video.instance.youtube_id, WORKING / video.instance.youtube_id
        )
        video.add_file(results[0])

    def download_info():
        info, files = get_video_info(video.instance.youtube_id)

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

        solara.Button(f"Download Info", on_click=download_info)
        solara.Button(f"Download Video", on_click=download_video)
        solara.Button(f"Create/Download Audio")
