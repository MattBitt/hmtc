from pathlib import Path

import solara
from loguru import logger

from hmtc.components.shared.my_spinner import MySpinner
from hmtc.components.video.jf_panel import JFPanel
from hmtc.components.video.section_dialog_button import SectionDialogButton
from hmtc.config import init_config
from hmtc.domains.series import Series as SeriesItem
from hmtc.domains.youtube_series import YoutubeSeries as YoutubeSeriesItem
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
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200
AVERAGE_SECTION_LENGTH = 180
IMG_WIDTH = "300px"
loading = solara.reactive(False)


@solara.component_vue("file_type_checkboxes.vue", vuetify=True)
def FileTypeCheckboxes(
    db_files,
    folder_files,
    has_audio: bool = False,
    has_video: bool = False,
    has_subtitle: bool = False,
    has_info: bool = False,
    has_poster: bool = False,
    has_album_nfo: bool = False,
    event_download_video: callable = None,
    event_download_info: callable = None,
    event_create_album_nfo: callable = None,
):
    pass


@solara.component
def FilesPanel(video):

    loading = solara.use_reactive(False)
    status_message = solara.use_reactive("")

    def download_info(*args):
        loading.set(True)
        VideoItem.refresh_youtube_info(video.id)
        VideoItem.create_album_nfo(video)
        loading.set(False)

    def download_video(*args):
        loading.set(True)
        logger.info(f"Downloading video: {video.title}")
        FileManager.remove_existing_files(
            video.id, video.youtube_id, ["video", "audio"]
        )
        info, files = download_video_file(video.youtube_id, WORKING, progress_hook=None)

        vid = VideoModel.select().where(VideoModel.id == video.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)
            # this is where i need to add the jellyfin id to the database,
            # but, i need to make sure that the video is in jellyfin first
        loading.set(False)

    file_types_found = [x.file_type for x in video.files]
    if loading.value:
        with solara.Row(justify="center"):
            MySpinner()
            solara.Text(f"{status_message.value}")
    else:

        FileTypeCheckboxes(
            db_files=[FileItem.from_model(x).serialize() for x in video.files],
            folder_files=[],
            has_audio="audio" in file_types_found,
            has_video="video" in file_types_found,
            has_info="info" in file_types_found,
            has_subtitle="subtitle" in file_types_found,
            has_poster="poster" in file_types_found,
            has_album_nfo="album_nfo" in file_types_found,
            event_download_video=download_video,
            event_create_album_nfo=lambda x: VideoItem.create_album_nfo(video),
            event_download_info=download_info,
        )
