import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.disc import Disc
from hmtc.domains.video import Video
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Disc as DiscModel,
)
from hmtc.models import (
    DiscVideo as DiscVideoModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.utils.general import paginate

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
def DiscCard(disc, refresh_counter):
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

    dv = (
        DiscVideoModel.select()
        .where(DiscVideoModel.disc_id == disc.instance.id)
        .first()
    )

    num_videos_on_disc = (
        DiscVideoModel.select(fn.COUNT(DiscVideoModel.id))
        .where(DiscVideoModel.disc_id == disc.instance.id)
        .scalar()
    )

    if num_videos_on_disc == 1:
        card_title = f"{disc.instance.order} - {dv.video.title}"
        disc_editor = {"display": "none"}
        # delete the following once it works
        disc_editor = {}
    else:
        card_title = f"{disc.instance.order}: ({num_videos_on_disc} Videos)"
        disc_editor = {}

    with solara.Card(f"{card_title}"):
        solara.Text(f"{disc.instance.folder_name}")
        with solara.Columns([6, 6]):
            with solara.Row():
                solara.Image(Video(dv.video).poster(thumbnail=True), width="150px")

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
                        disabled=disc.instance.order <= 1,
                    )
                    solara.Button(
                        "Move Down",
                        on_click=move_down,
                        classes=["button"],
                        disabled=disc.instance.order == 0,
                    )
                with solara.Column():
                    with solara.Link(f"/api/discs/details/{disc.instance.id}"):
                        solara.Button(
                            "Edit Disc", classes=["button"], style=disc_editor
                        )


@solara.component
def AlbumCard(album, refresh_counter):
    def reset_disc_numbers():
        logger.debug(f"Resetting the disc numbers")
        album.reset_disc_numbers()
        refresh_counter.set(refresh_counter.value + 1)

    def delete_discs():
        logger.debug(f"Deleting {album.instance.title}'s Discs")
        album.delete_discs()
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Row(justify="space-around"):
        solara.Button(
            f"Delete All Discs",
            icon_name="mdi-delete",
            on_click=delete_discs,
            classes=["button mywarning"],
        )
        solara.Markdown(f"# {album.instance.title}")
        solara.Button(
            f"Reset Disc Numbers", on_click=reset_disc_numbers, classes=["button"]
        )


@solara.component
def AlbumDiscs(query, current_page, num_pages, num_items, refresh_counter):

    PaginationControls(
        current_page=current_page, num_pages=num_pages, num_items=num_items
    )

    for disc in query:
        _disc = Disc(disc)
        DiscCard(_disc, refresh_counter)


@solara.component
def Page():
    router = solara.use_router()
    current_page = solara.use_reactive(1)
    refresh_counter = solara.use_reactive(1)
    per_page = 3
    _album = parse_url_args()
    query = (
        DiscModel.select()
        .where(DiscModel.album_id == _album.instance.id)
        .order_by(DiscModel.order)
    )

    _query, num_items, num_pages = paginate(
        query=query,
        page=current_page.value,
        per_page=per_page,
    )

    if current_page.value > num_pages:
        # if the query is updated and the 'current
        # page' is no longer valid, move to the
        # last page
        current_page.set(num_pages)

    with solara.Column(classes=["main-container"]):

        if len(_query) == 0:
            solara.Info(f"No Videos added to this album")
            return
        if refresh_counter.value > 0:
            AlbumDiscs(_query, current_page, num_pages, num_items, refresh_counter)
            AlbumCard(_album, refresh_counter)
