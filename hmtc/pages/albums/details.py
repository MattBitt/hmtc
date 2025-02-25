import solara
from loguru import logger
from peewee import fn

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import (
    DiscVideo as DiscVideoModel,
)

selected_videos = solara.reactive([])


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

    return _id


@solara.component
def DiscCard(disc: Disc, refresh_counter):
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

    def create_tracks():
        disc.create_tracks()

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
        solara.Text(f"{disc.instance.folder_name}")
        with solara.Columns([4, 8]):
            with solara.Row():
                if dv is not None and dv.video is not None:
                    solara.Image(Video(dv.video).poster(thumbnail=True), width="150px")
                else:
                    solara.Error(f"No Poster found...")

            with solara.Row():
                with solara.Column():
                    solara.Button(
                        "Delete Disc",
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

                    solara.Button(
                        "Create Tracks",
                        classes=["button"],
                        icon_name=Icons.TRACK.value,
                        on_click=create_tracks,
                    )


@solara.component
def AlbumCard(album: Album, refresh_counter):
    def reset_disc_numbers():
        logger.debug(f"Renumber Discs")
        album.reset_disc_numbers()
        refresh_counter.set(refresh_counter.value + 1)

    def delete_discs():
        logger.debug(f"Deleting {album.instance.title}'s Discs")
        album.delete_discs()
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Row(justify="space-around"):
        solara.Button(
            f"Delete All Discs",
            icon_name=Icons.DELETE.value,
            on_click=delete_discs,
            classes=["button mywarning"],
            disabled=True,
        )
        solara.Markdown(f"# {album.instance.title}")
        solara.Button(
            f"Reset Disc Numbers",
            on_click=reset_disc_numbers,
            classes=["button mywarning"],
            disabled=True,
        )


@solara.component
def AlbumDiscs(album: Album, refresh_counter):
    current_page = solara.use_reactive(1)

    album_discs, num_items, num_pages = album.discs_paginated(current_page, per_page=3)

    if len(album_discs) == 0:
        return solara.Info(f"No Discs added to this album")

    if current_page.value > num_pages:
        current_page.set(num_pages)

    for disc in album_discs:
        _disc = Disc(disc)
        DiscCard(_disc, refresh_counter)

    PaginationControls(
        current_page=current_page, num_pages=num_pages, num_items=num_items
    )


@solara.component
def AlbumDetails(album: Album):

    with solara.Card():
        with solara.Row(justify="center"):
            solara.Markdown(f"## {album.instance.title[:80]}")


@solara.component
def Page():

    refresh_counter = solara.use_reactive(1)

    _album = parse_url_args()

    with solara.Column(classes=["main-container"]):
        if refresh_counter.value > 0:
            AlbumCard(_album, refresh_counter)
            AlbumDiscs(_album, refresh_counter)
