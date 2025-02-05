from pathlib import Path

import solara
from flask import session
from loguru import logger

from hmtc.components.video.video_info_panel import VideoInfoPanel
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.domains.video import Video
from hmtc.utils.youtube_functions import download_video_file, get_video_info

config = init_config()
WORKING = config["WORKING"]


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


# http://localhost:5000/api/videos/details/1


@solara.component
def Page():
    router = solara.use_router()

    register_vue_components(file=__file__)
    if "current_user" in session:
        logger.debug(session["current_user"])
    else:
        logger.debug(f"No current user not currently in session dict")
        return

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
        solara.Text(f"Current visits in session {session['visits']}")
        solara.Button(
            f"Edit Sections ({len(sections)})",
            on_click=lambda: router.push(f"/utils/sectionalizer/{video.instance.id}"),
            classes=["button"],
        )
        solara.Markdown(f"## Files")
        for file in video.file_repo.my_files(video.instance.id):
            solara.Markdown(f"### {file['file']}")

        solara.Button(f"Download Info", on_click=download_info)
        solara.Button(f"Download Video", on_click=download_video)
        solara.Button(f"Create/Download Audio")
