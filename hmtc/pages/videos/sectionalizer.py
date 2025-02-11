import solara
from loguru import logger

from hmtc.components.sectionalizer import Sectionalizer
from hmtc.domains.video import Video


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


@solara.component
def Page():
    def create_section(section):
        logger.debug(f"Creating a section for {video} using args {section}")

    video_id = parse_url_args()
    video = Video(video_id)
    with solara.Column(classes=["main-container"]):
        Sectionalizer(video=video, create_section=create_section)
