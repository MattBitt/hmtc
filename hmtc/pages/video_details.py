from pathlib import Path
from datetime import timedelta, datetime
import PIL
import solara
from loguru import logger
from hmtc.assets.colors import Colors
from hmtc.components.shared.jellyfin_panel import JellyfinPanel
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import (
    File as FileModel,
)
from hmtc.models import (
    Series as SeriesModel,
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import (
    Video as VideoModel,
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


@solara.component_vue("../components/section/section_list_item.vue", vuetify=True)
def SectionListItem(items):
    pass


@solara.component_vue("../components/section/section_tabs.vue", vuetify=True)
def SectionTabs(tabItems, event_add_item, event_remove_item, event_delete_section):
    pass


@solara.component_vue("../components/section/section_info.vue", vuetify=True)
def SectionEditor(
    item: SectionModel = None,
    is_connected: bool = False,
    has_active_user_session: bool = False,
    play_status: bool = False,
    current_position: int = 0,
    event_save_section: callable = None,
    event_delete_section: callable = None,
    event_loop_jellyfin: callable = None,
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


# code from old NewJellyfinPanel lol
# exists = jf_client.value.search_media(video.youtube_id)
# if exists["TotalRecordCount"] > 0:
#     logger.debug(f"Found video {video.youtube_id} in Jellyfin")
#     logger.debug(f"Video jellyfin id = {exists['Items'][0]['Id']}")
#     # solara.Markdown("Found in Jellyfin")
# else:
#     logger.debug(f"Video {video.youtube_id} not found in Jellyfin")
#     # solara.Markdown("Not Found in Jellyfin")

# if jf_client.value.play_status == "stopped":
#     # no media item loaded
#     is_video_id_playing_in_jellyfin = False
# else:
#     is_video_id_playing_in_jellyfin = jf_client.value.media_item["Id"] == video.jellyfin_id


@solara.component
def NewJellyfinPanel(video, jellyfin_status):
    JF_LOGO_WIDTH = "80px"
    pth = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")
    jf_client = solara.use_reactive(None)
    play_state = solara.use_reactive("stopped")
    icon_color = solara.use_reactive("mywarning")

    def connect_jellyfin():
        jf_client.set(MyJellyfinClient())
        if jf_client.value.is_connected:
            jellyfin_status.set(dict(status="connected", color="mylight"))
            icon_color.set("mylight")
        else:
            jellyfin_status.set(dict(status="disconnected", color="myerror"))
            icon_color.set("myerror")

    def play_button():
        # adding on 9/28/24
        # want to load the item if its not already loaded
        if jf_client.value.play_status == "stopped":
            local_load_item()
            jf_client.value.play_pause()
        else:
            jf_client.value.play_pause()

    def local_load_item():
        if video.jellyfin_id is None:
            logger.error("No Jellyfin ID for this video")
            return
        jf_client.value.stop()
        jf_client.value.load_media_item(jellyfin_id=video.jellyfin_id)
        jf_client.value.play_pause()

    with solara.Columns([4, 8]):
        with solara.Column():
            solara.Image(pth, width=JF_LOGO_WIDTH, classes=[icon_color.value, "pa-1"])

        with solara.Column():
            if jf_client.value is None:
                logger.debug("Haven't tried connecting yet.")
                solara.Text(f"Not connected to Jellyfin.")
            else:
                if (
                    jf_client.value.is_connected
                    and jf_client.value.has_active_user_session
                ):
                    with solara.Row():
                        solara.Button(
                            label="",
                            icon_name="mdi-play-pause",
                            classes=["button"],
                            on_click=play_button,
                        )
                        solara.Button(
                            label="",
                            icon_name="mdi-stop",
                            classes=["button"],
                            disabled=not jf_client.value.play_status == "playing",
                        )
                else:
                    logger.debug("Jellyfin not connected/or no active")
                    solara.Text(
                        f"No Active Jellyfin sessions found for {jf_client.value.user}."
                    )
            solara.Button(
                label="",
                icon_name="mdi-refresh",
                classes=["button"],
                on_click=connect_jellyfin,
            )


@solara.component
def SectionCounter(sections):
    solara.Markdown(f"Num Sections: {len(sections.value)}")


@solara.component
def SectionControlPanel(
    video,
    sections,
    current_section,
    section_dicts,
    jellyfin_status,
):
    section_type = solara.use_reactive("intro")

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
        section_dicts.set(sections.value + [SectionManager.get_section_details(new_id)])
        logger.debug(f"New Section ID: {new_id}")

    def create_section_at_0():
        sm = SectionManager.from_video(video)
        new_sect_id = sm.create_section(
            start=0, end=AVERAGE_SECTION_LENGTH, section_type=section_type.value
        )
        new_sect = SectionModel.get_by_id(new_sect_id)
        sections.set(sections.value + [new_sect])

    def create_section_at_jellyfin_position():
        pass

    with solara.Column(align="center"):
        if num_sections.value > 0:
            with solara.Column(style={"width": "30%"}):
                solara.Button(
                    "Clear All Sections",
                    on_click=clear_all_sections,
                    outlined=True,
                    classes=["button mywarning"],
                )
        else:
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
                solara.Button(
                    label="Section at Jellyfin",
                    classes=["button"],
                    on_click=create_section_at_jellyfin_position,
                    disabled=(video.duration < AVERAGE_SECTION_LENGTH)
                    or (jellyfin_status.value["status"] == "initial"),
                )


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    # jellyfin_logo = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")
    check_icon = Path("./hmtc/public/icons/check.png")
    jellyfin_status = solara.use_reactive(dict(status="initial", color="mylight"))
    sm = SectionManager.from_video(video)
    reactive_sections = solara.use_reactive(sm.sections)
    # not sure why this is a tuple...
    section_dicts = (
        solara.use_reactive(
            [SectionManager.get_section_details(s.id) for s in reactive_sections.value]
        ),
    )
    files = FileModel.select().where(FileModel.video_id == video.id)
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
    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))
    IMG_WIDTH = "200px"

    def download_video(*args):
        logger.info(f"Downloading video: {video.title}")
        info, files = download_video_file(
            video.youtube_id, WORKING, progress_hook=my_hook
        )

        vid = VideoModel.select().where(VideoModel.id == video.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)

    def delete_section(*args, **kwargs):
        for section in reactive_sections.value:
            logger.debug(f"Deleting Section: {args}")
            delete_section_from_db(args[0]["section_id"])
            reactive_sections.set(
                [s for s in reactive_sections.value if s.id != args[0]["section_id"]]
            )

    def create_album_nfo(*args):
        new_file = VideoItem.create_xml_for_jellyfin(video.id)
        FileManager.add_path_to_video(new_file, video)

    def update_series(*args):
        logger.debug(f"Updating Series: {args}")
        series = SeriesModel.select().where(SeriesModel.name == args[0]).get()
        vid = VideoModel.get_by_id(video.id)
        vid.series = series
        vid.save()

    def update_youtube_series(*args):
        logger.debug(f"Updating Youtube Series: {args}")
        youtube_series = (
            YoutubeSeriesModel.select().where(YoutubeSeriesModel.title == args[0]).get()
        )
        vid = VideoModel.get_by_id(video.id)
        vid.youtube_series = youtube_series
        vid.save()

    with solara.Column(classes=["main-container"]):
        with solara.Column(classes=["py-0", "px-4"]):
            with solara.Columns([6, 6]):
                with solara.Columns([6, 6]):
                    with solara.Column():

                        solara.Image(image, width=IMG_WIDTH)
                        solara.Text(
                            f"{video.title[:60]}",
                            classes=["video-info-text"],
                        )

                    with solara.Column():
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

                        with solara.Column(classes=["mt-2"]):
                            solara.Text(
                                f"Uploaded: {time_ago_string(video.upload_date)}",
                                classes=["medium-timer"],
                            )
                            solara.Text(
                                f"Length: {seconds_to_hms(video.duration)}",
                                classes=["medium-timer"],
                            )

                with solara.Column():
                    NewJellyfinPanel(video=video, jellyfin_status=jellyfin_status)
                    FileTypeCheckboxes(
                        has_audio="audio" in [f.file_type for f in files],
                        has_video="video" in [f.file_type for f in files],
                        has_info="info" in [f.file_type for f in files],
                        has_subtitle="subtitle" in [f.file_type for f in files],
                        has_poster="poster" in [f.file_type for f in files],
                        has_album_nfo="album_nfo" in [f.file_type for f in files],
                        event_download_video=download_video,
                        event_create_album_nfo=create_album_nfo,
                        event_download_info=lambda x: VideoItem.refresh_youtube_info(
                            video.id
                        ),
                    )

        # with solara.Row():
        #     with solara.Card():
        #         if video.album is not None:
        #             poster = FileManager.get_file_for_album(video.album, "poster")
        #             image = PIL.Image.open(Path(str(poster)))
        #             # solara.Image(image, width="200px")
        #             solara.Text(f"{video.album.title}")
        #             solara.Image(check_icon, width="50px")
        #         else:
        #             solara.Markdown("No Album")
        #             solara.Button("Add Album", classes=["button"])

        with solara.Column(classes=["mysurface"], style={"height": "800px"}):
            SectionControlPanel(
                video=video,
                sections=reactive_sections,
                current_section=None,
                section_dicts=section_dicts,
                jellyfin_status=jellyfin_status,
            )
            if len(sm.sections) > 0:

                SectionTabs(
                    tabItems=section_dicts[0].value,
                    event_add_item=add_topic,
                    event_remove_item=remove_topic,
                    event_delete_section=delete_section,
                )

            else:

                solara.Markdown("No Sections Found")
