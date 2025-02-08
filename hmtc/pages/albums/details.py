import solara
from loguru import logger

from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.album import Album
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
    return _id


@solara.component
def DiscCard(disc):
    with solara.Card(f"{disc.title}"):
        disc_videos = DiscVideoModel.select().where(DiscVideoModel.disc_id == disc.id)
        for dv in disc_videos:
            solara.Text(f"{dv.video.title}")


@solara.component
def Page():

    router = solara.use_router()
    album_id = parse_url_args()
    current_page = solara.use_reactive(1)

    try:
        _album = Album(album_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        with solara.Error(f"Video Id {album_id} not found."):
            with solara.Link("/"):
                solara.Button("Home", classes=["button"])
        return

    discs = DiscModel.select().where(DiscModel.album_id == _album.instance.id)

    query, num_items, num_pages = paginate(
        query=discs,
        page=current_page.value,
        per_page=12,
    )

    with solara.Column(classes=["main-container"]):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )
        if len(discs) == 0:
            solara.Info(f"No Videos added to this album")
            return

        solara.Text(f"{_album.instance.title}")
        with solara.ColumnsResponsive():
            for disc in query:
                DiscCard(disc)
