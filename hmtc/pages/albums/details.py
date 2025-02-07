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

def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id

@solara.component
def Page():
    with solara.Column(classes=["main-container"]):
        solara.Text(f"Album Editor Page")
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


    base_query = (
        DiscModel.select()
        .join(DiscVideoModel, on=(DiscVideoModel.video_id == DiscModel.id))
        .join(VideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
        .where(DiscModel.album_id == _album.instance.id)
    )
    
    for item in base_query:
        solara.Text(f"{item}")
