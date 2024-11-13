from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.video.lower_sections_panel import LowerSectionsPanel
from hmtc.components.video.video_info_panel import VideoInfoPanelLeft
from hmtc.components.video.no_sections_panel import NoSectionsPanel
from hmtc.components.video.top_row import TopRow
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import (
    File as FileModel,
)
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
)
from hmtc.models import (
    Series as SeriesModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.section import SectionManager
from hmtc.schemas.series import Series as SeriesItem
from hmtc.schemas.track import Track as TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.schemas.youtube_series import YoutubeSeries as YoutubeSeriesItem
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200
AVERAGE_SECTION_LENGTH = 180
IMG_WIDTH = "300px"

loading = solara.reactive(False)


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        router.push("/videos")
    else:
        return router.parts[level:][0]
    logger.error(f"Does this execute? {router.parts}")


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)

    register_vue_components(file=__file__)

    video_id = parse_url_args()
    if video_id is None or video_id == 0:
        with solara.Error():
            solara.Markdown(f"No Video Found {video_id}")
        return

    video = VideoItem.from_model(VideoModel.get_by_id(video_id))
    sections = SectionModel.select().where(SectionModel.video_id == video.id)
    reactive_sections = solara.use_reactive(
        [SectionItem.from_model(s) for s in sections]
    )
    with solara.Column(classes=["main-container"]):

        TopRow(
            video=video,
            reactive_sections=reactive_sections,
        )

        with solara.Row():
            VideoInfoPanelLeft(video=video)

        if len(reactive_sections.value) == 0:
            NoSectionsPanel(
                video=video,
            )
        else:
            LowerSectionsPanel(
                video=video,
                reactive_sections=reactive_sections,
            )
