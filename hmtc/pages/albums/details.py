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
from hmtc.pages.albums.video_selector import VideoSelector

selected_videos = solara.reactive([])


@solara.component
def Page():
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Album Editor Page")
    router = solara.use_router()
    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Title", "value": "title", "width": "30%"},
        {"text": "Order", "value": "order", "sortable": True},
    ]
    _album = AlbumModel.select().get()
    album = Album(_album)
    base_query = (
        VideoModel.select()
        .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
        .join(DiscModel, on=(DiscModel.id == DiscVideoModel.disc_id))
        .where(DiscModel.album_id == album.instance.id)
    )
    search_fields = [VideoModel.title]
    VideoSelector(album=album)
