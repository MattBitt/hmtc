from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.video.jf_panel import JFPanel
from hmtc.config import init_config
from hmtc.domains.album import Album as AlbumItem
from hmtc.domains.section import Section as SectionItem
from hmtc.domains.series import Series as SeriesItem
from hmtc.domains.track import Track as TrackItem
from hmtc.domains.video import Video as VideoItem
from hmtc.domains.youtube_series import YoutubeSeries as YoutubeSeriesItem
from hmtc.models import Album as AlbumModel
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopic as SectionTopicsModel,
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
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.youtube_functions import download_video_file


@solara.component_vue("../section/SectionControlPanel.vue", vuetify=True)
def SectionControlPanel(
    video,
    jellyfin_status,
    event_delete_all_sections,
    event_create_section,
):
    pass


@solara.component
def SectionDialogButton(video, reactive_sections):
    def delete_all_sections(*args):
        logger.error(f"Deleting all Sections {args}")

    def create_section(*args):
        logger.error(f"Create Section {args}")
        pass

    SectionControlPanel(
        video=VideoItem.serialize(video),
        jellyfin_status={"status": "offline"},
        event_create_section=create_section,
        event_delete_all_sections=delete_all_sections,
    )
