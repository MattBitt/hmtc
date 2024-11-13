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


@solara.component_vue("VideoInfoInputCard.vue")
def VideoInfoInputCard(
    albums,
    serieses,
    youtube_serieses,
    selectedAlbum,
    selectedSeries,
    selectedYoutubeSeries,
    episode_number,
    event_create,
    event_update,
    event_remove,
):
    pass


@solara.component_vue("../section/SectionControlPanel.vue", vuetify=True)
def SectionControlPanel(
    video,
    jellyfin_status,
    event_delete_all_sections,
    event_create_section,
):
    pass


@solara.component_vue("JellyfinControlPanel.vue")
def JellyfinControlPanel(
    enable_live_updating,
    jellyfin_status,
    event_update_play_state=None,
):
    pass


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
        page_jellyfin_id=video.jellyfin_id,
        api_key=config["jellyfin"]["api"],
        event_update_play_state=refresh_from_jellyfin,
    )


@solara.component
def InfoPanel(
    video,
):
    force_update_counter = solara.use_reactive(0)
    vid_db = VideoModel.get_by_id(video.id)

    def create(*args):
        logger.debug(f"Generic Create Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.create(**item)
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.create(**item)
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.create(**item)
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            return

    def update(*args):
        logger.debug(f"Generic Update Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]

        except Exception as e:
            logger.error(e)
            raise

        try:
            match _type:
                case "album":
                    item_id = AlbumModel.get_by_id(item["id"])
                    vid_db.album = item_id
                    vid_db.save()
                    album_item = AlbumItem.from_model(item_id)
                    # i think leaving this here will change the album poster
                    # every time the album is updated
                    album_item.use_video_poster()

                case "series":
                    item_id = SeriesModel.get_by_id(item["id"])
                    vid_db.series = item_id
                    vid_db.save()

                case "youtube_series":
                    item_id = YoutubeSeriesModel.get_by_id(item["id"])
                    vid_db.youtube_series = item_id
                    vid_db.save()

                case _:
                    logger.error(f"Type {_type} not found")
                    return
            force_update_counter.set(force_update_counter.value + 1)

        except Exception as e:
            logger.error(e)
            raise

    def remove(*args):
        logger.debug(f"Generic Remove Function: {args}")

        try:
            _type = args[0]["type"]
            item = args[0]["item"]
        except Exception as e:
            logger.error(e)
            return

        try:
            match _type:
                case "album":
                    vid_db.album = None
                    vid_db.save()
                    AlbumItem.delete_if_unused(item["id"])

                case "series":
                    vid_db.series = None
                    vid_db.save()
                    SeriesItem.delete_if_unused(item["id"])
                case "youtube_series":
                    vid_db.youtube_series = None
                    vid_db.save()
                    YoutubeSeriesItem.delete_if_unused(item["id"])
                case _:
                    logger.error(f"Type {_type} not found")
                    return

        except Exception as e:
            logger.error(e)
            return

        vid_db.save()
        logger.debug(f"Successfully removed item from video {args}")

    album_dicts = [
        dict(id=a.id, title=a.title)
        for a in AlbumModel.select().order_by(AlbumModel.title)
    ]

    youtube_series_dicts = [
        dict(id=a.id, title=a.title)
        for a in YoutubeSeriesModel.select().order_by(YoutubeSeriesModel.title)
    ]
    series_dicts = [
        dict(id=a.id, name=a.name)
        for a in SeriesModel.select().order_by(SeriesModel.name)
    ]

    try:
        this_album = [a for a in album_dicts if a["id"] == video.album_id][0]
    except IndexError:
        this_album = {"id": 0, "title": "None"}

    try:
        this_youtube_series = [
            x for x in youtube_series_dicts if x["id"] == video.youtube_series_id
        ][0]
    except IndexError:
        this_youtube_series = None

    try:
        this_series = [x for x in series_dicts if x["id"] == video.series_id][0]
    except IndexError:
        this_series = None

    VideoInfoInputCard(
        albums=album_dicts,
        youtube_serieses=youtube_series_dicts,
        serieses=series_dicts,
        selectedAlbum=this_album,
        selectedYoutubeSeries=this_youtube_series,
        selectedSeries=this_series,
        episode_number=video.episode,
        event_create=create,
        event_update=update,
        event_remove=remove,
    ),


@solara.component
def FilesPanel(video):
    files = FileModel.select().where(FileModel.video_id == video.id)
    loading = solara.use_reactive(False)
    status_message = solara.use_reactive("")

    def download_info(*args):
        loading.set(True)
        FileManager.remove_existing_files(
            video.id, video.youtube_id, ["info", "subtitle", "poster"]
        )
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

    db_files, folder_files = FileManager.get_video_files(video.id, video.youtube_id)
    ff_serialized = [dict(name=x.name) for x in folder_files]
    file_types_found = [x.file_type for x in files]
    if loading.value:
        with solara.Row(justify="center"):
            MySpinner()
            solara.Text(f"{status_message.value}")
    else:

        FileTypeCheckboxes(
            db_files=[FileItem.from_model(x).serialize() for x in db_files],
            folder_files=ff_serialized,
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


@solara.component
def UpperSectionPanel(video, reactive_sections):
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


@solara.component
def TopRow(video, reactive_sections):
    # VideoInfoInputCard.vue
    # Buttons 1, 2, 3
    with solara.Row(justify="center"):
        InfoPanel(
            video=video,
        )
        # Button 4
        FilesPanel(
            video=video,
        )
        # Button 5
        UpperSectionPanel(
            video=video,
            reactive_sections=reactive_sections,
        )
        # Button 6 (jellyfin icon)
        JFPanel(
            video=video,
        )
