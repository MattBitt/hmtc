from pathlib import Path

import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.vue_registry import register_vue_components
from hmtc.config import init_config
from hmtc.domains.series import Series as SeriesItem
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
from hmtc.schemas.track import Track as TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.schemas.youtube_series import YoutubeSeries as YoutubeSeriesItem
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.time_functions import seconds_to_hms, time_ago_string
from hmtc.utils.youtube_functions import download_video_file


@solara.component
def NoSectionsPanel(video):
    with solara.Card(title="No Sections"):
        if video.album_id is not None:
            solara.Markdown(f"Album: {video.album_id}")
        else:
            solara.Markdown(f"## Please Create an album before adding sections")
