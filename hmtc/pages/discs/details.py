import solara
from loguru import logger
from peewee import fn

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
    disc: Disc,
    video: Video,
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")

    def move_up():

        album = Album(disc.instance.album)
        album.move_disc_up(disc)
        refresh_counter.set(refresh_counter.value + 1)

    def move_down():

        album = Album(disc.instance.album)
        album.move_disc_down(disc)
        refresh_counter.set(refresh_counter.value + 1)

    def remove_video():
        # since this is a single video disc
        # i should delete the disc

        disc.delete()
        refresh_counter.set(refresh_counter.value + 1)

    num_videos_on_disc = (
        DiscVideoModel.select(fn.COUNT(DiscVideoModel.id))
        .where(DiscVideoModel.disc_id == disc.instance.id)
        .scalar()
    )
    order = DiscVideoModel.select(DiscVideoModel.order).where(
        (DiscVideoModel.video_id == video.instance.id)
        & (DiscVideoModel.disc_id == disc.instance.id)
    ).get().order
    if num_videos_on_disc == 1:
        card_title = f"{video.instance.title}"
        disc_editor = {"display": "none"}
        # delete the following once it works
        disc_editor = {}
    else:

        card_title = f"{order}: ({num_videos_on_disc} Videos)"
        disc_editor = {}

    with solara.Card(f"{card_title}"):
        solara.Text(f"{disc.instance.folder_name}")
        with solara.Columns([6, 6]):
            with solara.Row():
                solara.Image(video.poster(thumbnail=True), width="150px")

            with solara.Row():
                with solara.Column():
                    solara.Button(
                        "Delete Disc",
                        on_click=remove_video,
                        classes=["button mywarning"],
                        icon_name="mdi-delete",
                    )
                with solara.Column():
                    solara.Button(
                        "Move Up",
                        on_click=move_up,
                        classes=["button"],
                        disabled= order ==  1,
                    )
                    solara.Button(
                        "Move Down",
                        on_click=move_down,
                        classes=["button"],
                        disabled=order == 0,
                    )
                with solara.Column():
                    with solara.Link(f"/api/discs/details/{disc.instance.id}"):
                        solara.Button(
                            "Edit Disc", classes=["button"], style=disc_editor
                        )

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
        per_page=3,
    )

    if current_page.value > num_pages:
        current_page.set(num_pages)

    with solara.Row(justify="center"):
        MainRow(disc)

    for video in _query:
        SecondRow(disc, Video(video))
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
