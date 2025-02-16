from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.my_spinner import MySpinner
from hmtc.config import init_config
from hmtc.domains.album import Album as AlbumItem
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

config = init_config()
WORKING = Path(config["WORKING"]) / "downloads"
STORAGE = Path(config["STORAGE"]) / "videos"


@solara.component_vue("JellyfinControlPanel.vue")
def JellyfinControlPanel(
    enable_live_updating,
    jellyfin_status,
    event_update_play_state=None,
):
    pass


@solara.component
def JFPanel(
    video,
):

    def refresh_from_jellyfin(*args):
        jellyfin_status_dict.set(get_user_session())

    connected = solara.use_reactive(can_ping_server())
    jellyfin_status_dict = solara.use_reactive(get_user_session())

    JellyfinControlPanel(
        enable_live_updating=connected.value,
        jellyfin_status=jellyfin_status_dict.value,
        page_jellyfin_id=video.instance.jellyfin_id,
        api_key=config["jellyfin"]["api"],
        event_update_play_state=refresh_from_jellyfin,
    )
