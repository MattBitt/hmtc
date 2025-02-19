import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel

refresh_counter = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


@solara.component
def DiscVideoCard(
    disc: Disc,
    video: Video,
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")

    def move_up():

        disc.move_video_up(video)
        refresh_counter.set(refresh_counter.value + 1)

    def move_down():

        disc.move_video_down(video)
        refresh_counter.set(refresh_counter.value + 1)

    def remove_video():

        disc.remove_video(video)
        refresh_counter.set(refresh_counter.value + 1)

    num_videos_on_disc = disc.num_videos_on_disc()
    order = (
        DiscVideoModel.select(DiscVideoModel.order)
        .where(
            (DiscVideoModel.video_id == video.instance.id)
            & (DiscVideoModel.disc_id == disc.instance.id)
        )
        .get()
        .order
    )

    if num_videos_on_disc == 1:
        card_title = f"{video.instance.title} (only video on this disc)"

    else:
        card_title = f"Video {order}: {disc.instance.title}"

    with solara.Card(title=f"{card_title}", subtitle=f"{disc.instance.folder_name}"):
        with solara.Columns([4, 8]):
            with solara.Row():
                solara.Image(video.poster(thumbnail=True), width="150px")

            with solara.Row():
                with solara.Column():
                    solara.Button(
                        "Remove Video",
                        on_click=remove_video,
                        classes=["button mywarning"],
                        icon_name=Icons.DELETE.value,
                    )
                with solara.Column():
                    solara.Button(
                        "Move Up",
                        on_click=move_up,
                        icon_name=Icons.UP_BOX.value,
                        classes=["button"],
                        disabled=order == 1,
                    )
                    solara.Button(
                        "Move Down",
                        on_click=move_down,
                        icon_name=Icons.DOWN_BOX.value,
                        classes=["button"],
                        disabled=order == num_videos_on_disc,
                    )
                with solara.Column():
                    with solara.Link(f"/api/videos/details/{video.instance.id}"):
                        solara.Button(
                            "Details", icon_name=Icons.SECTION.value, classes=["button"]
                        )


@solara.component
def MainRow(disc: Disc):
    if disc.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return

    num_videos_on_disc = disc.num_videos_on_disc()
    with solara.Card():
        with solara.Row(justify="center"):
            solara.Markdown(
                f"## {disc.instance.album.title} - {disc.instance.title} ({num_videos_on_disc} Videos) "
            )


@solara.component
def DiscDetails(disc: Disc):
    current_page = solara.use_reactive(1)

    disc_vids, num_items, num_pages = disc.videos_paginated(current_page, per_page=3)

    if len(disc_vids) == 0:
        return solara.Warning(f"No Videos found for {disc}")

    if current_page.value > num_pages:
        current_page.set(num_pages)

    with solara.Row(justify="center"):
        MainRow(disc)

    for video in disc_vids:
        DiscVideoCard(disc, Video(video))
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
        if refresh_counter.value > 0:
            DiscDetails(disc)
