import time

import solara
from loguru import logger

from hmtc.components.fine_tuner import FineTuner
from hmtc.domains.video import Video
from hmtc.utils.jellyfin_functions import (
    jf_playpause,
    load_media_item,
    search_for_media,
)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")

    try:
        video = Video(_id)

    except Exception as e:
        logger.error(f"Exception {e}")

    return video


@solara.component
def Page():

    video = parse_url_args()
    # using this page to fine tune sections
    # auto load the video in jellyfin if possible
    media = search_for_media("videos", video.instance.youtube_id)
    load_media_item(media["Id"])
    time.sleep(0.1)
    jf_playpause()

    with solara.Column(classes=["main-container"]):
        FineTuner(video)
