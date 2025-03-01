import shutil
from pathlib import Path

import solara
from loguru import logger
from peewee import fn

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import (
    DiscVideo as DiscVideoModel,
)
from hmtc.models import Video as VideoModel
from hmtc.repos.file_repo import get_filetype

selected_videos = solara.reactive([])

config = init_config()

STORAGE = Path(config["STORAGE"]) / "libraries"
WORKING = Path(config["WORKING"])


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")

    _album = Album(_id)
    try:
        _album = Album(_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        raise ValueError(f"Album with ID {_id} NOT found")
    return _album


# show one of these for each disc in the album (if unlocked)
# paginated
@solara.component
def DiscCard(disc: Disc, refresh_counter):

    has_tracks = solara.use_reactive(disc.tracks().exists())
    num_sections = disc.num_sections()
    num_sections_ft = disc.num_sections(fine_tuned=True)

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

    num_videos_on_disc = disc.num_videos_on_disc()
    if num_videos_on_disc == 1:
        card_title = f"{disc.instance.order} - {dv.video.title[:40]}"

    else:
        card_title = f"{disc.instance.order}: ({num_videos_on_disc} Videos)"

    with solara.Card(f"{card_title}"):
        with solara.Row():
            solara.Text(f"{disc.instance.folder_name}")
            solara.Text(f"{num_sections=} {num_sections_ft=}")
        with solara.Columns([2, 10]):
            with solara.Row():
                solara.Image(disc.poster(thumbnail=True), width="150px")

            with solara.Row():
                with solara.Column():
                    solara.Button(
                        "Delete Disc",
                        on_click=remove_disc,
                        classes=["button mywarning"],
                        icon_name=Icons.DELETE.value,
                    )
                with solara.Column():
                    solara.Button(
                        "Move Up",
                        on_click=move_up,
                        icon_name=Icons.UP_BOX.value,
                        classes=["button"],
                        disabled=disc.instance.order <= 1,
                    )
                    solara.Button(
                        "Move Down",
                        on_click=move_down,
                        icon_name=Icons.DOWN_BOX.value,
                        classes=["button"],
                        disabled=disc.instance.order == 0,
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
                            "Delete Tracks",
                            classes=["button mywarning"],
                            icon_name=Icons.TRACK.value,
                            on_click=remove_tracks,
                        )

                        solara.Button(
                            f"Create Tracks ({num_sections_ft if num_sections > 0 else ""})",
                            classes=["button"],
                            icon_name=Icons.TRACK.value,
                            on_click=create_tracks,
                            disabled=(num_sections_ft == 0),
                        )


# shows at the top of the page. controls locking/unlocking discs
@solara.component
def AlbumCard(
    album: Album, refresh_counter: solara.Reactive, discs_locked: solara.Reactive
):

    poster = solara.use_reactive(album.poster())

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

                solara.Button(
                    f"Reset Disc Numbers",
                    on_click=reset_disc_numbers,
                    classes=["button mywarning"],
                    disabled=True,
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
def AlbumDiscsSummary(album: Album, refresh_counter: solara.Reactive):
    solara.Text(f"{album.instance.title} {refresh_counter.value} Summary")
    first_vid = Video(album.instance.discs[0].dv.first().video_id)
    total_video_duration = (
        VideoModel.select(fn.SUM(VideoModel.duration))
        .where(VideoModel.id.in_(album.discs_and_videos()))
        .scalar()
    )
    with solara.Columns([6, 6]):
        solara.Image(first_vid.poster(thumbnail=False), width="450px")
        with solara.Column():
            with solara.Row():
                solara.Text(
                    f"{album.videos_count()} videos", classes=["video-info-text"]
                )
                solara.Text(
                    f"{total_video_duration} seconds ", classes=["video-info-text"]
                )
            with solara.Row():
                solara.Text(
                    f"{album.tracks_count()} tracks", classes=["video-info-text"]
                )
                solara.Text(
                    f"{album.track_duration()} seconds", classes=["video-info-text"]
                )

                if total_video_duration > 0:
                    solara.Text(
                        f"{album.track_duration()/total_video_duration}",
                        classes=["video-info-text"],
                    )


@solara.component
def AlbumDiscs(
    album: Album, refresh_counter: solara.Reactive, discs_locked: solara.Reactive
):
    current_page = solara.use_reactive(1)

    album_discs, num_items, num_pages = album.discs_paginated(current_page, per_page=3)

    if len(album_discs) == 0:
        return solara.Info(f"No Discs added to this album")

    if current_page.value > num_pages:
        current_page.set(num_pages)
    with SwapTransition(show_first=discs_locked.value, name="fade"):

        with solara.Card():
            AlbumDiscsSummary(album, refresh_counter)

        with solara.Card():
            for disc in album_discs:
                _disc = Disc(disc)
                DiscCard(_disc, refresh_counter)

            PaginationControls(
                current_page=current_page, num_pages=num_pages, num_items=num_items
            )


@solara.component
def Page():

    refresh_counter = solara.use_reactive(1)

    _album = parse_url_args()
    discs_locked = solara.use_reactive(_album.instance.discs_order_locked)
    with solara.Column(classes=["main-container"]):
        if refresh_counter.value > 0:
            AlbumCard(_album, refresh_counter, discs_locked)
            AlbumDiscs(_album, refresh_counter, discs_locked)
