import solara
from loguru import logger

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
    try:
        _album = Album(album_id)
    except Exception as e:
        logger.error(f"Exception {e}")
        with solara.Error(f"Video Id {album_id} not found."):
            with solara.Link("/"):
                solara.Button("Home", classes=["button"])
        return

    discs = DiscModel.select().where(DiscModel.album_id == _album.instance.id)
    with solara.Column(classes=["main-container"]):
        solara.Text(f"{_album.instance.title}")
        with solara.ColumnsResponsive():
            for disc in discs.limit(20):
                DiscCard(disc)
