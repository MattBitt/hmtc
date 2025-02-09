import solara
from loguru import logger

from hmtc.components.sectionalizer.main import VideoFrame
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.utils.general import paginate

refresh_counter = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


@solara.component
def SecondRow(
    video: Video,
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")
    with solara.Card():
        solara.Text(f"Video: {video.instance.title}")


@solara.component
def MainRow(disc: Disc):
    if disc.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return
    with solara.Card():
        with solara.Row(justify="center"):
            solara.Text(f"{disc.instance.title}")
            solara.Text(f"{disc.instance.album.title}")


@solara.component
def DiscEditor(disc: Disc):
    current_page = solara.use_reactive(1)
    disc_vids = DiscVideoModel.select(DiscVideoModel.video_id).where(
        DiscVideoModel.disc_id == disc.instance.id
    )

    page_query = VideoModel.select().where(VideoModel.id.in_(disc_vids))
    if len(page_query) == 0:
        solara.Warning(f"No Discs Found meeting these criteria.")
        return

    _query, num_items, num_pages = paginate(
        query=page_query,
        page=current_page.value,
        per_page=12,
    )

    if current_page.value > num_pages:
        current_page.set(num_pages)

    with solara.Row(justify="center"):
        MainRow(disc)

    for video in _query:
        SecondRow(Video(video))
    with solara.Row(justify="center"):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )


@solara.component
def Page():
    disc_id = parse_url_args()
    try:
        disc = Disc(disc_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        with solara.Error(f"Disc Id {disc_id} not found."):
            with solara.Link("/"):
                solara.Button("Home", classes=["button"])
        return
    with solara.Column(classes=["main-container"]):
        # if refresh_counter.value > 0:
        DiscEditor(disc)
