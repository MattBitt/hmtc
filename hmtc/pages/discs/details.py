import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel

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
        card_title = f"Video {order}: {video.instance.title[:40]}"

    with solara.Card(title=f"{card_title}", subtitle=f"{disc.instance.folder_name}"):
        with solara.Row():
            solara.Text(f"{video.instance.upload_date}")
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
def CheckVideoOrderButton(
    disc: Disc, checked: solara.Reactive, video_order_correct: solara.Reactive
):
    num_vids = disc.num_videos_on_disc()
    if num_vids == 1:
        solara.Text(f"Only 1 disc. Nothing to do")
        return

    def check():
        vids = disc.videos()
        date1 = vids[0].upload_date
        for vid in vids[1:]:
            if vid.upload_date > date1:
                date1 = vid.upload_date
            else:
                video_order_correct.set(False)

        if video_order_correct.value is None:
            video_order_correct.set(True)

        checked.set(True)

    solara.Button(
        f"Check the order of the {num_vids} videos", classes=["button"], on_click=check
    )


@solara.component
def ResetVideoOrderButton(disc: Disc):
    num_vids = int(disc.num_videos_on_disc())

    if num_vids == 1:
        solara.Text(f"Only 1 disc. Nothing to do")
        return

    def reset():
        counter = num_vids * 10  # just making room for the new ones
        dvs = (
            DiscVideoModel.select()
            .where(DiscVideoModel.disc_id == disc.instance.id)
            .order_by(DiscVideoModel.order)
        )
        vid_ids = [x.video.id for x in dvs]
        for dv in dvs:
            # update the order to a temp number for all of them
            # starting at temp_counter
            dv.order = counter
            dv.save()
            counter += 1
        vids_in_order = (
            VideoModel.select()
            .where(VideoModel.id.in_(vid_ids))
            .order_by(VideoModel.upload_date.asc())
        )

        counter = 1
        for vid in vids_in_order:
            dv = (
                DiscVideoModel.select()
                .where(
                    (DiscVideoModel.disc_id == disc.instance.id)
                    & (DiscVideoModel.video_id == vid.id)
                )
                .get()
            )
            dv.order = counter
            dv.save()
            counter += 1

    solara.Button(
        f"Reset Video Order ({num_vids} videos)",
        classes=["button mywarning"],
        on_click=reset,
    )


@solara.component
def MainRow(disc: Disc):

    video_order_correct = solara.use_reactive(None)
    checked = solara.use_reactive(False)
    if disc.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return

    num_videos_on_disc = disc.num_videos_on_disc()
    with solara.Row():
        with solara.Columns([6, 6]):
            with solara.Column():
                with SwapTransition(show_first=(checked.value == False), name="fade"):
                    CheckVideoOrderButton(disc, checked, video_order_correct)
                    with SwapTransition(
                        show_first=(video_order_correct.value == False)
                    ):
                        ResetVideoOrderButton(disc)
                        solara.Success(f"All Good!")

            with solara.Column():
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
