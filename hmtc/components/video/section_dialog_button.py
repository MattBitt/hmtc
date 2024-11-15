from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.video.jf_panel import JFPanel
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
    jellyfin_status_dict = solara.use_reactive(get_user_session())

    def delete_all_sections(*args):
        if len(reactive_sections.value) == 0:
            return

        for section in reactive_sections.value:
            logger.debug(f"Deleting Section: {section}")
            SectionItem.delete_id(section.id)

        reactive_sections.set([])

    def create_section(video, start, end, section_type="instrumental"):
        sm = SectionManager.from_video(video)
        new_sect_id = sm.create_section(start=start, end=end, section_type=section_type)
        new_sect = SectionModel.get_by_id(new_sect_id)
        reactive_sections.set(reactive_sections.value + [new_sect])

    def local_create(*args):
        logger.debug(f"Creating Section: {args}")
        create_section(video, args[0]["start"], args[0]["end"])

    SectionControlPanel(
        video=video.serialize(),
        jellyfin_status=jellyfin_status_dict.value,
        event_create_section=local_create,
        event_delete_all_sections=delete_all_sections,
    )
