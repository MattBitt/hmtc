import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.domains.video import VideoItem
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.utils.jellyfin_functions import get_currently_playing, load_media_item


def parse_url_args():
    router = solara.use_router()

    if len(router.parts) == 1:
        router.push("/")

    match router.parts:
        case ["segment-editor", segment_id]:
            return (
                SuperchatSegmentModel.select()
                .where(SuperchatSegmentModel.id == segment_id)
                .first()
            )
        case _:
            logger.error(f"Invalid URL: {router.parts}")
            router.push("/")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    seg = parse_url_args()
    segment = SuperchatSegmentItem.from_model(seg)
    jf = get_currently_playing()
    vid = VideoModel.get_by_id(segment.video_id)

    video = VideoItem.from_model(vid)
    image = segment.get_image()
    with solara.Row(justify="space-between"):
        solara.Image(image, width="600px")
        with solara.Column():
            JFPanel(video=video)
            solara.Button(
                f"Load in JF",
                on_click=lambda: load_media_item(video.jellyfin_id),
                classes=["button"],
            )
    solara.Text(f"Segment ID: {segment.id}")
