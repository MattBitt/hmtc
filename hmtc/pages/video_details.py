import time
from datetime import datetime, timedelta
from pathlib import Path

import ipyvue
import PIL
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
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
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.section import SectionManager
from hmtc.schemas.video import VideoItem
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200
AVERAGE_SECTION_LENGTH = 300
IMG_WIDTH = "500px"  # this isn't actually true on ipad, but it seems to look good

loading = solara.reactive(False)
jellyfin_status = solara.reactive(
    dict(
        status="initial",
        color="mylight",
        client=None,
        video_jellyfin_id=None,
        current_position=None,
    )
)


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        # solara.Markdown("No Video Selected")
        # raise ValueError("No video selected")
        # use this to view all sections
        return None

    return router.parts[level:][0]


def seconds_to_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


def my_hook(*args):
    # this seems to work but not getting the feedback on the page
    pass
    # d = args[0]["downloaded_bytes"]
    # t = args[0]["total_bytes"]
    # p = d / t * 100
    # if p < 1:
    #     logger.info(f"Percent Complete: {d/t*100:.2f}%")
    # current_download_progress.set(p)


def add_topic(*args):
    section_id = args[0]["item_id"]
    topic = args[0]["topic"]
    if section_id is None or topic is None:
        logger.error("Section ID or Topic is None")
        return
    topic, created = TopicModel.get_or_create(text=topic)
    if created:
        logger.debug(f"Created topic {topic.text}")
    _order = (
        SectionTopicsModel.select()
        .where(SectionTopicsModel.section_id == section_id)
        .count()
    )
    SectionTopicsModel.create(
        section_id=section_id, topic_id=topic.id, order=_order + 1
    )
    logger.debug(f"adding topic {topic} to section {section_id}")
    # t, created = TopicModel.get_or_create(text=args[0])
    # if created:
    #     logger.debug(f"Created topic {t.text}")
    # SectionTopicsModel.create(
    #     section_id=section.id, topic_id=t.id, order=15
    # )
    pass


def remove_topic(*args):
    section_id = args[0]["item_id"]
    topic = args[0]["topic"]
    logger.debug(f"remove_topic: {topic} from seciton {section_id}")

    t = TopicModel.select().where(TopicModel.text == topic).get_or_none()
    if t is None:
        logger.error(f"Topic {args[0]} not found")
        return

    SectionTopicsModel.delete().where(
        (SectionTopicsModel.section_id == section_id)
        & (SectionTopicsModel.topic_id == t.id)
    ).execute()

    topic_still_needed = SectionTopicsModel.get_or_none(
        SectionTopicsModel.topic_id == t.id
    )
    if topic_still_needed is None:
        logger.debug(f"Topic no longer needed {t.text} ({t.id}). Removing.")
        t.delete_instance()

    logger.error(f"Removed topic {t.text} ({t.id}) from section {section_id}")


def delete_section_from_db(section_id):
    logger.debug(f"Deleting Section: {section_id}")
    # need to delete topics first (as-needed)
    SectionModel.delete_by_id(section_id)


def time_ago_string(dt):
    time_ago = datetime.now().date() - dt
    logger.debug(time_ago)
    if time_ago.days == 0:
        return "Today"
    if time_ago.days < 30:
        if time_ago.days == 1:
            return "Yesterday"
        else:
            return f"{time_ago.days} days ago"
    if time_ago.days < 365:
        months = time_ago.days // 30
        if months == 1:
            return "Last month"
        else:
            return f"{months} months ago"
    years = time_ago.days // 365
    if years == 1:
        return "Last year"
    else:
        return f"{years} years ago"


def update_section_times(*args):
    logger.debug(f"Updating Section Times: {args}")
    section = SectionModel.get_by_id(args[0]["item_id"])
    section.start = args[0]["start"]
    section.end = args[0]["end"]
    section.save()


def loop_jellyfin(jellyfin_status, *args):
    logger.debug(f"Looping Jellyfin: {jellyfin_status} {args}")
    jf_client = MyJellyfinClient()
    jf_client.connect()
    jf_client.seek_to(args[0])
    jf_client.play_pause()
    time.sleep(1.5)
    jf_client.play_pause()


def update_section_from_jellyfin(section_id, start_or_end, video, reactive_sections):
    jf = MyJellyfinClient()
    jf.connect()
    if jf.is_connected:
        loading.set(True)
        new_position = jf.get_playing_status_from_jellyfin()["position"]
        sect = SectionModel.get_by_id(section_id)
        if start_or_end == "start":
            sect.start = new_position * 1000
        else:
            sect.end = new_position * 1000
        sect.save()
        new_sm = SectionManager.from_video(video)
        reactive_sections.set(new_sm.sections)
        # logger.debug(f"Updated Section {sect.id} to {new_position}")
    else:
        logger.error("No Jellyfin connection. Quitting")
    loading.set(False)


@solara.component_vue("../components/section/section_tabs.vue", vuetify=True)
def SectionTabs(
    tabItems,
    jellyfin_status,
    event_add_item,
    event_remove_item,
    event_delete_section,
    event_update_times,
    event_loop_jellyfin,
    event_update_section_from_jellyfin,
):
    pass


@solara.component_vue("../components/file/file_type_checkboxes.vue", vuetify=True)
def FileTypeCheckboxes(
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


@solara.component_vue("../components/shared/jellyfin_control_panel.vue")
def JellyfinControlPanel(
    session_id,
    jellyfin_id,
    is_server_connected,
    has_active_session,
    event_open_detail_page,
    event_open_video_in_jellyfin,
    event_playpause_jellyfin,
    event_stop_jellyfin,
    api_key,
):
    pass


@solara.component
def SectionControlPanel(
    video,
    sections,
    current_section,
    section_dicts,
    jellyfin_status,
):
    section_type = solara.use_reactive("intro")
    logger.debug(f"Jellyfin Status at SectionControlPanel: {jellyfin_status.value}")
    # existing sections
    num_sections = solara.use_reactive(len(sections.value))

    def clear_all_sections():
        for section in sections.value:
            logger.debug(f"Deleting Section: {section}")
            delete_section_from_db(section.id)

        sections.set([])

    def create_1_section():
        sm = SectionManager.from_video(video)
        new_sect_id = sm.create_section(
            start=0, end=video.duration, section_type=section_type.value
        )
        new_sect = SectionModel.get_by_id(new_sect_id)
        sections.set(sections.value + [new_sect])

    def split_into():
        # returns the number of whole sections
        sm = SectionManager.from_video(video)
        number_of_even_sections = (
            video.duration // AVERAGE_SECTION_LENGTH
        )  # 5 minute sections

        for i in range(number_of_even_sections):
            new_id = sm.create_section(
                start=i * (video.duration / number_of_even_sections),
                end=(i + 1) * (video.duration / number_of_even_sections),
                section_type="instrumental",
            )
        new_sect = SectionModel.get_by_id(new_id)
        sections.set(sm.sections + [new_sect])
        # section_dicts.set(sections.value + [SectionManager.get_section_details(new_id)])
        logger.debug(f"New Section ID: {new_id}")

    def create_section_at_0():
        sm = SectionManager.from_video(video)
        new_sect_id = sm.create_section(
            start=0, end=AVERAGE_SECTION_LENGTH, section_type=section_type.value
        )
        new_sect = SectionModel.get_by_id(new_sect_id)
        sections.set(sections.value + [new_sect])

    def create_section_at_jellyfin_position():
        jf = MyJellyfinClient()
        jf.connect()
        status = jf.get_playing_status_from_jellyfin()
        try:
            pos = status["position"]

        except Exception as e:
            logger.error(f"Error getting position from Jellyfin: {e}")
            return

        sm = SectionManager.from_video(video)
        section_end = (
            (pos + AVERAGE_SECTION_LENGTH)
            if pos + AVERAGE_SECTION_LENGTH < video.duration
            else video.duration
        )
        new_sect_id = sm.create_section(
            start=pos,
            end=section_end,
            section_type=section_type.value,
        )
        new_sect = SectionModel.get_by_id(new_sect_id)
        sections.set(sections.value + [new_sect])

    with solara.Column(align="center"):
        with solara.Row():
            solara.Button(
                "1 Section",
                on_click=create_1_section,
                classes=["button"],
                disabled=(video.duration > MAX_SECTION_LENGTH),
            )
            solara.Button(
                f"{video.duration // AVERAGE_SECTION_LENGTH} sections",
                on_click=split_into,
                classes=["button"],
                disabled=(video.duration < AVERAGE_SECTION_LENGTH),
            )
            solara.Button(
                label="Section at 0",
                classes=["button"],
                on_click=create_section_at_0,
                disabled=(video.duration < AVERAGE_SECTION_LENGTH),
            )
            # logger.debug(f"Jellyfin Status: {jellyfin_status.value}")
        with solara.Row():
            solara.Button(
                label="Section at Jellyfin",
                classes=["button"],
                on_click=create_section_at_jellyfin_position,
            )
            if num_sections.value > 0:
                solara.Button(
                    "Clear All Sections",
                    on_click=clear_all_sections,
                    outlined=True,
                    classes=["button mywarning"],
                )


@solara.component
def JFPanel(
    video,
    jellyfin_status,
    router,
    update_section_from_jellyfin,
):
    def vue_link_clicked(item):
        # need to add a check to make sure the route is existing
        if item is not None:
            try:
                playing_vid = (
                    VideoModel.select(VideoModel.id)
                    .where(VideoModel.jellyfin_id == item)
                    .get_or_none()
                )
                router.push(f"/video-details/{playing_vid.id}")
            except Exception as e:
                logger.error(e)

    jf = MyJellyfinClient()
    try:
        jf.connect()
    except Exception as e:
        logger.error(f"Error connecting to Jellyfin from Video Details Page: {e}")

    if jf.has_active_session():
        session_id = jf.active_session["Id"]
    else:
        session_id = ""

    JellyfinControlPanel(
        is_server_connected=jf.is_connected,
        has_active_session=jf.has_active_session(),
        can_seek=jf.can_seek,
        session_id=session_id,
        jellyfin_id=video.jellyfin_id,
        event_update_section_from_jellyfin=update_section_from_jellyfin,
        event_open_detail_page=vue_link_clicked,
        event_open_video_in_jellyfin=lambda x: jf.load_media_item(video.jellyfin_id),
        event_pause_jellyfin=lambda x: jf.pause(),
        event_playpause_jellyfin=lambda x: jf.play_pause(),
        event_stop_jellyfin=lambda x: jf.stop(),
        api_key=config["jellyfin"]["api"],
    )


@solara.component
def FilesPanel(video):
    files = FileModel.select().where(FileModel.video_id == video.id)

    def download_video(*args):
        logger.info(f"Downloading video: {video.title}")
        info, files = download_video_file(
            video.youtube_id, WORKING, progress_hook=my_hook
        )

        vid = VideoModel.select().where(VideoModel.id == video.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)
            # this is where i need to add the jellyfin id to the database,
            # but, i need to make sure that the video is in jellyfin first

    def create_album_nfo(*args):
        new_file = VideoItem.create_xml_for_jellyfin(video.id)
        FileManager.add_path_to_video(new_file, video)

    FileTypeCheckboxes(
        has_audio="audio" in [f.file_type for f in files],
        has_video="video" in [f.file_type for f in files],
        has_info="info" in [f.file_type for f in files],
        has_subtitle="subtitle" in [f.file_type for f in files],
        has_poster="poster" in [f.file_type for f in files],
        has_album_nfo="album_nfo" in [f.file_type for f in files],
        event_download_video=download_video,
        event_create_album_nfo=create_album_nfo,
        event_download_info=lambda x: VideoItem.refresh_youtube_info(video.id),
    )


@solara.component
def InfoPanel(
    video,
):

    def update_youtube_series(*args):
        logger.debug(f"Updating Youtube Series: {args}")
        youtube_series = (
            YoutubeSeriesModel.select().where(YoutubeSeriesModel.title == args[0]).get()
        )
        vid = VideoModel.get_by_id(video.id)
        vid.youtube_series = youtube_series
        vid.save()

    def update_series(*args):
        logger.debug(f"Updating Series: {args}")
        series = SeriesModel.select().where(SeriesModel.name == args[0]).get()
        vid = VideoModel.get_by_id(video.id)
        vid.series = series
        vid.save()

    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))

    serieses = [
        item.model_to_dict()["name"]
        for item in SeriesModel.select(SeriesModel.name).order_by(SeriesModel.name)
    ]
    series_name = solara.reactive(video.series.name if video.series else None)
    youtube_serieses = [
        item.model_to_dict()["title"]
        for item in YoutubeSeriesModel.select(YoutubeSeriesModel.title).order_by(
            YoutubeSeriesModel.title
        )
    ]
    youtube_series_title = solara.reactive(
        video.youtube_series.title if video.youtube_series else None
    )

    with solara.Row():
        solara.Image(image, width=IMG_WIDTH)
        with solara.Column():
            solara.Select(
                label="Series",
                values=serieses,
                value=series_name,
                on_value=update_series,
            )
            solara.Select(
                label="Youtube Series",
                values=youtube_serieses,
                value=youtube_series_title,
                on_value=update_youtube_series,
            )
    with solara.Row():
        solara.Text(
            f"{video.title[:50]}",
            classes=["video-info-text"],
        )

    with solara.Row():
        solara.Text(
            f"Uploaded: {time_ago_string(video.upload_date)}",
            classes=["medium-timer"],
        )
        solara.Text(
            f"Length: {seconds_to_hms(video.duration)}",
            classes=["medium-timer"],
        )


@solara.component
def SectionsPanel(
    sm,
    video,
    reactive_sections,
    jellyfin_status,
    update_section_from_jellyfin,
):

    # not sure why this is a tuple...
    section_dicts = (
        solara.use_reactive(
            [SectionManager.get_section_details(s.id) for s in reactive_sections.value]
        ),
    )

    def delete_section(*args, **kwargs):
        logger.debug(f"Deleting Section: {args}")
        delete_section_from_db(args[0]["section_id"])
        reactive_sections.set(
            [s for s in reactive_sections.value if s.id != args[0]["section_id"]]
        )

    if len(sm.sections) > 0:

        SectionTabs(
            tabItems=section_dicts[0].value,
            jellyfin_status=jellyfin_status.value,
            event_add_item=add_topic,
            event_remove_item=remove_topic,
            event_delete_section=delete_section,
            event_update_times=update_section_times,
            event_loop_jellyfin=lambda x: loop_jellyfin(jellyfin_status, x),
            event_update_section_from_jellyfin=update_section_from_jellyfin,
        )

    else:

        solara.Markdown("No Sections Found")
    SectionControlPanel(
        video=video,
        sections=reactive_sections,
        current_section=None,
        section_dicts=section_dicts,
        jellyfin_status=jellyfin_status,
    )


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    ipyvue.register_component_from_file(
        "MyToolTipChip",
        "../components/my_tooltip_chip.vue",
        __file__,
    )

    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    sm = SectionManager.from_video(video)
    reactive_sections = solara.use_reactive(sm.sections)

    def local_update_from_jellyfin(*args):
        update_section_from_jellyfin(
            args[0]["section"], args[0]["start_or_end"], video, reactive_sections
        )

    with solara.Column(classes=["main-container"]):
        with solara.Column(classes=["py-0", "px-4", "mysurface"]):
            with solara.Columns([7, 5]):
                with solara.Column():
                    InfoPanel(
                        video=video,
                    )
                with solara.Column():
                    JFPanel(
                        video=video,
                        jellyfin_status=jellyfin_status,
                        router=router,
                        update_section_from_jellyfin=local_update_from_jellyfin,
                    )
                    FilesPanel(
                        video=video,
                    )
        with solara.Column(classes=["py-0", "px-4", "mysurface"]):
            SectionsPanel(
                sm=sm,
                video=video,
                reactive_sections=reactive_sections,
                jellyfin_status=jellyfin_status,
                update_section_from_jellyfin=local_update_from_jellyfin,
            )
