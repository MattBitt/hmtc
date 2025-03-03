import shutil
from pathlib import Path

import solara
from loguru import logger
from peewee import fn

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.check_and_fix.main import CheckAndFix
from hmtc.components.function_button.main import FunctionButton
from hmtc.components.shared import Chip, MyList, PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.track import Track
from hmtc.domains.video import Video
from hmtc.models import Disc as DiscModel
from hmtc.models import (
    DiscVideo as DiscVideoModel,
)
from hmtc.models import Video as VideoModel
from hmtc.repos.file_repo import get_filetype
from hmtc.utils.time_functions import seconds_to_hms

refresh_counter = solara.reactive(1)


config = init_config()

STORAGE = Path(config["STORAGE"]) / "libraries"
WORKING = Path(config["WORKING"])


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")

    return Album(_id)


# show one of these for each disc in the album (if unlocked)
# paginated
@solara.component
def AlbumDiscCard(disc: Disc):

    has_tracks = solara.use_reactive(disc.tracks().exists())

    def move_up():

        album = Album(disc.instance.album)
        album.move_disc_up(disc)
        refresh_counter.set(refresh_counter.value + 1)

    def move_down():

        album = Album(disc.instance.album)
        album.move_disc_down(disc)
        refresh_counter.set(refresh_counter.value + 1)

    def remove_disc():
        disc.delete()
        refresh_counter.set(refresh_counter.value + 1)

    def create_tracks():
        disc.create_tracks()
        refresh_counter.set(refresh_counter.value + 1)

    def remove_tracks():
        disc.remove_tracks()
        refresh_counter.set(refresh_counter.value + 1)

    dv = (
        DiscVideoModel.select()
        .where(DiscVideoModel.disc_id == disc.instance.id)
        .first()
    )

    def move_to_compilation_disc():

        album = Album(disc.instance.album.id)
        album.move_disc_to_compilation(disc)

        refresh_counter.set(refresh_counter.value + 1)

    num_videos_on_disc = disc.num_videos_on_disc()
    if num_videos_on_disc == 1:
        card_title = f"{disc.instance.order} - {dv.video.title[:40]}"

    else:
        card_title = f"{disc.instance.order}: ({num_videos_on_disc} Videos)"

    disable_move_to_comp = (num_videos_on_disc > 1) or disc.instance.title == "Disc 000"

    with solara.Columns([8, 4]):
        with solara.Column():
            with solara.Row():
                solara.Text(f"{card_title}")
            with solara.Row():
                if disc.instance.xlarge:
                    Chip("X-LARGE")

                Chip(f"{seconds_to_hms(disc.video_duration())}", color="info")
                Chip(f"S/FT/T")
                Chip(
                    f"{disc.num_sections()}/{disc.num_sections(fine_tuned=True)}/{disc.num_tracks()}",
                    color=disc.section_status_color(),
                )

            with solara.Columns([2, 3, 3, 4]):
                with solara.Column():
                    solara.Image(disc.poster(thumbnail=True), width="100px")

                with solara.Column():
                    solara.Button(
                        on_click=remove_disc,
                        classes=["button mywarning"],
                        icon_name=Icons.DISC.value,
                    )
                    solara.Button(
                        "Comp",
                        on_click=move_to_compilation_disc,
                        classes=["button"],
                        icon_name=Icons.MOVE.value,
                        disabled=disable_move_to_comp,  # already a compilation
                    )
                with solara.Column():
                    solara.Button(
                        on_click=move_up,
                        icon_name=Icons.UP_BOX.value,
                        classes=["button"],
                        disabled=(disc.instance.order <= 1) or (disc.num_tracks() > 0),
                    )
                    solara.Button(
                        on_click=move_down,
                        icon_name=Icons.DOWN_BOX.value,
                        classes=["button"],
                        disabled=(disc.instance.order == 0) or (disc.num_tracks() > 0),
                    )
                with solara.Column():
                    if num_videos_on_disc == 1:

                        with solara.Link(f"/api/videos/details/{dv.video.id}"):
                            solara.Button(
                                "Details",
                                classes=["button"],
                                icon_name=Icons.VIDEO.value,
                            )

                    else:

                        with solara.Link(f"/api/discs/details/{disc.instance.id}"):
                            solara.Button(
                                "Details",
                                classes=["button"],
                                icon_name=Icons.DISC.value,
                            )
                    with SwapTransition(show_first=has_tracks.value, name="fade"):
                        solara.Button(
                            "Tracks",
                            classes=["button mywarning"],
                            icon_name=Icons.DELETE.value,
                            on_click=remove_tracks,
                        )
                        if disc.num_sections() == 0:
                            caption = "No Sections"
                        elif disc.num_sections(fine_tuned=True) == 0:
                            caption = "No Sections FT"
                        else:
                            caption = f"Tracks ({disc.num_sections(fine_tuned=True)})"

                        solara.Button(
                            label=caption,
                            classes=["button"],
                            icon_name=Icons.TRACK.value,
                            on_click=create_tracks,
                            disabled=({disc.num_sections(fine_tuned=True)} == 0),
                        )
        with solara.Column():
            if disc.num_videos_on_disc() == 1:
                if disc.num_tracks() > 0:
                    _tracks = [t.title for t in disc.tracks()[:4]]

                    MyList(title="Tracks", items=_tracks)
                else:
                    Chip("No Tracks Created", color="warning")
            else:
                with solara.Row():
                    Chip(f"{disc.num_videos_on_disc()} Videos", color="info")
                    Chip(f"{seconds_to_hms(disc.video_duration())}", color="info")
                with solara.Row():
                    Chip(f"{disc.num_tracks()} Tracks", color="info")
                    Chip(f"{seconds_to_hms(disc.tracks_duration())}", color="info")


def check_disc_order(album: Album):
    logger.debug(f"Checking {album}")
    result = album.is_disc_order_correct()
    return result


def fix_disc_order(album: Album):
    logger.debug(f"Fixing {album}")
    album.reset_disc_numbers()
    refresh_counter.set(refresh_counter.value + 1)


def has_tracks_to_create(album: Album):
    return not album.has_tracks_to_create()


def create_tracks(album: Album):
    album.create_tracks()
    refresh_counter.set(refresh_counter.value + 1)


def delete_tracks(album: Album):
    for _disc in album.discs():
        disc = Disc(_disc.id)
        disc.remove_tracks()

    refresh_counter.set(refresh_counter.value + 1)


# shows at the top of the page. controls locking/unlocking discs
@solara.component
def AlbumCard(album: Album, discs_locked: solara.Reactive):

    poster = solara.use_reactive(album.poster())
    num_tracks = album.num_tracks()

    def lock_discs():
        album.lock_discs()
        discs_locked.set(True)
        refresh_counter.set(refresh_counter.value + 1)

    def unlock_discs():
        album.unlock_discs()
        discs_locked.set(False)
        refresh_counter.set(refresh_counter.value + 1)

    def reset_disc_numbers():
        logger.debug(f"Renumber Discs")
        album.reset_disc_numbers()
        refresh_counter.set(refresh_counter.value + 1)

    def delete_discs():
        logger.debug(f"Deleting {album.instance.title}'s Discs")
        album.delete_discs()
        refresh_counter.set(refresh_counter.value + 1)

    def add_poster(file):
        logger.debug(file)

        ft = get_filetype(file["name"])
        if ft != "poster":
            logger.error(f"Only taking posters. Not {ft} {file}")
            return

        new_file = WORKING / "poster.jpg"
        new_file2 = WORKING / "poster2.jpg"

        with open(new_file, "wb") as f:
            f.write(file["file_obj"].read())

        shutil.copy(new_file, new_file2)

        album.add_file(new_file, "video")
        album.add_file(new_file2, "audio")

        logger.debug(f"Adding poster to {album} {ft}")
        poster.set(album.poster())

    def remove_poster():
        album.file_repo.delete(album.instance.id, "poster")
        poster.set("Placeholder Image")

    def move_short_vids():
        discs = DiscModel.select().where(DiscModel.album_id == album.instance.id)
        for _disc in discs:
            disc = Disc(_disc)
            if disc.num_videos_on_disc() != 1:
                continue

            video = disc.videos()[0]
            if video.duration > 600:  # 10 minutes
                continue

            album.move_disc_to_compilation(disc)
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Row(justify="space-around"):
        with solara.Columns([4, 4, 4]):
            with solara.Column():
                solara.Button(
                    f"Delete All Discs",
                    icon_name=Icons.DELETE.value,
                    on_click=delete_discs,
                    classes=["button mywarning"],
                    disabled=True,
                )

                CheckAndFix(
                    album,
                    check_label="Check Video Order",
                    check_icon=Icons.DISC.value,
                    check_function=check_disc_order,
                    repair_label="Fix Video Order",
                    repair_icon=Icons.REPAIR.value,
                    repair_function=fix_disc_order,
                    repair_class="mywarning",
                    success_message="All Videos are in Order",
                )

                CheckAndFix(
                    album,
                    check_label="New Tracks?",
                    check_icon=Icons.TRACK.value,
                    check_function=has_tracks_to_create,
                    repair_label="Create Tracks",
                    repair_icon=Icons.TRACK.value,
                    repair_function=create_tracks,
                    repair_class="mywarning",
                    success_message="No Tracks to Create!",
                )

            with SwapTransition(show_first=poster.value is not None, name="fade"):
                with solara.Column():
                    solara.Markdown(f"# {album.instance.title}")
                    solara.Image(poster.value, width="300px")
                with solara.Column():
                    solara.Markdown(f"# {album.instance.title}")
                    solara.Markdown(f"# No poster found. Add one now!")

            with solara.Column():
                with SwapTransition(show_first=discs_locked.value, name="fade"):
                    solara.Button(
                        f"Unlock Discs",
                        on_click=unlock_discs,
                        icon_name=Icons.UNLOCK.value,
                        classes=["button"],
                    )
                    solara.Button(
                        f"Lock Discs",
                        on_click=lock_discs,
                        icon_name=Icons.LOCK.value,
                        classes=["button"],
                    )
                with SwapTransition(
                    show_first=poster.value == "Placeholder Image", name="fade"
                ):
                    solara.FileDrop(
                        label=f"Add a Poster for {album.instance.title}!",
                        on_file=add_poster,
                        lazy=True,
                    )
                    solara.Button(
                        f"Delete the album poster.",
                        on_click=remove_poster,
                        classes=["button"],
                    )


# shows when the discs have been locked. can assume at least
# 1 disc exists
@solara.component
def AlbumDiscsSummary(album: Album):
    solara.Text(f"{album.instance.title} {refresh_counter.value} Summary")

    total_video_duration = (
        VideoModel.select(fn.SUM(VideoModel.duration))
        .where(VideoModel.id.in_(album.discs_and_videos()))
        .scalar()
    )
    if total_video_duration is None:
        total_video_duration = 0

    with solara.Columns([6, 6]):
        solara.Image(album.poster(thumbnail=False), width="450px")
        with solara.Column():
            with solara.Row():
                solara.Text(
                    f"{album.videos_count()} videos", classes=["video-info-text"]
                )
                solara.Text(
                    f"{total_video_duration} seconds ", classes=["video-info-text"]
                )
            with solara.Row():
                solara.Text(f"{album.num_tracks()} tracks", classes=["video-info-text"])
                solara.Text(
                    f"{album.track_duration()} seconds", classes=["video-info-text"]
                )

                if total_video_duration > 0:
                    solara.Text(
                        f"{album.track_duration()/total_video_duration}",
                        classes=["video-info-text"],
                    )


@solara.component
def AlbumDiscs(album: Album, discs_locked: solara.Reactive):
    current_page = solara.use_reactive(1)

    album_discs, num_items, num_pages = album.discs_paginated(current_page, per_page=3)

    if len(album_discs) == 0:
        return solara.Info(f"No Discs added to this album")

    if current_page.value > num_pages:
        current_page.set(num_pages)

    with SwapTransition(show_first=discs_locked.value, name="fade"):

        with solara.Card():
            AlbumDiscsSummary(album)
        # list of album discs
        with solara.Card():
            for disc in album_discs:
                _disc = Disc(disc)
                AlbumDiscCard(_disc)
            with solara.Row(justify="center"):
                PaginationControls(
                    current_page=current_page, num_pages=num_pages, num_items=num_items
                )


@solara.component
def Page():

    album = parse_url_args()
    discs_locked = solara.use_reactive(album.instance.discs_order_locked)

    with solara.Column(classes=["main-container"]):
        if refresh_counter.value > 0:
            AlbumCard(album, discs_locked)
            AlbumDiscs(album, discs_locked)
