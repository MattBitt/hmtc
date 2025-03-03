import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.check_and_fix.main import CheckAndFix
from hmtc.components.shared import Chip, MyList, PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Video as VideoModel
from hmtc.utils.time_functions import seconds_to_hms

refresh_counter = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")

    return Disc(_id)


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

    def move_to_new_disc():
        from hmtc.domains.album import Album

        disc.remove_video(video)
        album = Album(disc.instance.album.id)
        album.add_video(video.instance)
        refresh_counter.set(refresh_counter.value + 1)

    def use_poster():
        disc.use_poster_from_video(video)
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

    with solara.Columns([8, 4]):
        with solara.Column():
            with solara.Row():
                solara.Text(f"{card_title}")
            with solara.Row():
                Chip(f"{video.instance.upload_date}")
                Chip(f"{seconds_to_hms(video.instance.duration)}")
                Chip(f"S/FT/T")
                Chip(
                    f"{video.num_sections()}/{video.num_sections(fine_tuned=True)}/{video.num_tracks()}",
                    color=video.section_status_color(),
                )

            with solara.Columns([2, 2, 3, 5]):
                with solara.Column():
                    p = video.poster(thumbnail=True)

                    with solara.Row(justify="center"):
                        solara.Image(p, width="100px")
                    with solara.Row(justify="center"):
                        solara.Button(
                            icon_name=Icons.IMAGE.value,
                            classes=["button"],
                            on_click=use_poster,
                        )

                with solara.Column():
                    solara.Button(
                        on_click=remove_video,
                        classes=["button mywarning"],
                        icon_name=Icons.VIDEO.value,
                    )
                    solara.Button(
                        "New Disc",
                        on_click=move_to_new_disc,
                        classes=["button"],
                        icon_name=Icons.MOVE.value,
                    )
                with solara.Column():
                    solara.Button(
                        on_click=move_up,
                        icon_name=Icons.UP_BOX.value,
                        classes=["button"],
                        disabled=(order == 1) or disc.num_tracks() > 0,
                    )
                    solara.Button(
                        on_click=move_down,
                        icon_name=Icons.DOWN_BOX.value,
                        classes=["button"],
                        disabled=(order == num_videos_on_disc) or disc.num_tracks() > 0,
                    )
                with solara.Column():
                    with solara.Link(f"/api/videos/details/{video.instance.id}"):
                        solara.Button(
                            "Details",
                            icon_name=Icons.VIDEO.value,
                            classes=["button"],
                        )

        with solara.Column():
            if video.num_tracks() > 0:
                _tracks = [t.title for t in video.tracks()[:4]]

                MyList(title="Tracks", items=_tracks)
            else:
                Chip("No Tracks Created", color="warning")


def check(disc: Disc):
    vids = disc.videos()
    date1 = vids[0].upload_date
    for vid in vids[1:]:
        if vid.upload_date > date1:
            date1 = vid.upload_date
        else:
            return False
    return True


def reset(disc: Disc):

    num_vids = int(disc.num_videos_on_disc())

    if num_vids == 1:
        solara.Text(f"Only 1 disc. Nothing to do")
        return

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


@solara.component
def Poster(disc, poster):
    with SwapTransition(show_first=poster.value is not None, name="fade"):
        with solara.Column():
            solara.Markdown(f"# {disc.instance.title}")
            solara.Image(poster.value, width="300px")
        with solara.Column():
            solara.Markdown(f"# {disc.instance.title}")
            solara.Markdown(f"# No poster found. Add one now!")


@solara.component
def DiscCard(disc: Disc):
    poster = solara.use_reactive(disc.poster())

    def clickme():
        pass

    def remove_poster():
        disc.file_repo.delete(disc.instance.id, "poster")
        poster.set("Placeholder Image")

    num_videos_on_disc = disc.num_videos_on_disc()
    with solara.Row(justify="space-around"):
        with solara.Columns([4, 4, 4]):
            with solara.Column():
                CheckAndFix(
                    disc,
                    check_label="Check Video Order",
                    check_icon=Icons.DISC.value,
                    check_function=check,
                    repair_label="Fix Video Order",
                    repair_icon=Icons.DELETE.value,
                    repair_function=reset,
                )
            with solara.Column():
                Poster(disc, poster)

            with solara.Column():
                solara.Markdown(f"## {disc.instance.album.title[:40]}")
                solara.Markdown(
                    f"{disc.instance.title[:40]} ({num_videos_on_disc} Videos)"
                )

                with SwapTransition(
                    show_first=poster.value == "Placeholder Image", name="fade"
                ):
                    # solara.FileDrop(
                    #     label=f"Add a Poster for {disc.instance.title}!",
                    #     on_file=clickme,
                    #     lazy=True,
                    # )
                    solara.Markdown(f"FileDrop Not implemented for discs.")
                    solara.Button(
                        f"Poster",
                        on_click=remove_poster,
                        classes=["button mywarning"],
                        icon_name=Icons.DELETE.value,
                    )


@solara.component
def DiscVideos(disc: Disc):
    current_page = solara.use_reactive(1)

    disc_vids, num_items, num_pages = disc.videos_paginated(current_page, per_page=3)

    if len(disc_vids) == 0:
        return solara.Warning(f"No Videos found for {disc}")

    if current_page.value > num_pages:
        current_page.set(num_pages)

    # list of disc videos
    for video in disc_vids:
        DiscVideoCard(disc, Video(video))
    with solara.Row(justify="center"):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )


@solara.component
def Page():

    disc = parse_url_args()

    with solara.Column(classes=["main-container"]):
        if refresh_counter.value > 0:
            with solara.Card():
                DiscCard(disc)
                DiscVideos(disc)
