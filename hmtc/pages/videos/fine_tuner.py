import solara
from loguru import logger

from hmtc.components.fine_tuner import FineTuner
from hmtc.domains.video import Video


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
    with solara.Column(classes=["main-container"]):
        FineTuner(video)
