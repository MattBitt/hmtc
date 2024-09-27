import solara
from pathlib import Path
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.section import Section as SectionItem
from hmtc.schemas.video import VideoItem
from hmtc.schemas.file import FileManager
import PIL
from hmtc.models import (
    Video as VideoModel,
    Section,
    File as FileModel,
    Topic as TopicModel,
    SectionTopics as SectionTopicsModel,
)
from hmtc.components.shared.jellyfin_panel import JellyfinPanel
from hmtc.models import Section as SectionModel
from hmtc.schemas.section import SectionManager
from hmtc.config import init_config
from loguru import logger
from hmtc.utils.youtube_functions import download_video_file


config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"
MIN_SECTION_LENGTH = 60
MAX_SECTION_LENGTH = 1200


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


@solara.component_vue("../components/section/section_list_item.vue", vuetify=True)
def SectionListItem(items):
    pass


@solara.component_vue("../components/section/section_tabs.vue", vuetify=True)
def SectionTabs(tabItems, event_add_item, event_remove_item, event_delete_section):
    pass


@solara.component_vue("../components/section/section_info.vue", vuetify=True)
def SectionEditor(
    item: Section = None,
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


@solara.component_vue("../components/chips/series.vue", vuetify=True)
def SeriesChip(series):
    pass


@solara.component_vue("../components/chips/playlist.vue", vuetify=True)
def PlaylistChip(playlist):
    pass


@solara.component_vue("../components/chips/album.vue", vuetify=True)
def AlbumChip(album):
    pass


@solara.component_vue("../components/chips/youtube_series.vue", vuetify=True)
def YoutubeSeriesChip(youtube_series):
    pass


@solara.component_vue("../components/chips/channel.vue")
def ChannelChip(channel):
    pass


@solara.component_vue("../components/shared/carousel.vue")
def Carousel(sections: list = []):
    pass


@solara.component
def NewJellyfinPanel(jf, video):
    def local_load_item():
        if video.jellyfin_id is None:
            logger.error("No Jellyfin ID for this video")
            return
        jf.stop()
        jf.load_media_item(jellyfin_id=video.jellyfin_id)
        jf.play_pause()

    exists = jf.search_media(video.youtube_id)
    if exists["TotalRecordCount"] > 0:
        logger.debug(f"Found video {video.youtube_id} in Jellyfin")
        logger.debug(f"Video jellyfin id = {exists['Items'][0]['Id']}")
        #solara.Markdown("Found in Jellyfin")
    else:
        logger.debug(f"Video {video.youtube_id} not found in Jellyfin")
        #solara.Markdown("Not Found in Jellyfin")

    if jf.play_status == "stopped":
        # no media item loaded
        is_video_id_playing_in_jellyfin = False
    else:
        is_video_id_playing_in_jellyfin = jf.media_item["Id"] == video.jellyfin_id

    pth = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")
        
    if jf.is_connected and jf.has_active_user_session:
        solara.Image(pth, width="80px", classes=["mydark", "pa-2"])
        solara.Markdown(f"Jellyfin Connected: {jf.is_connected}")

        logger.debug(f"Jellyfin Session ID: {jf.session_id}")
        solara.Markdown(f"**{jf.user}**")

        with solara.Row():
            if is_video_id_playing_in_jellyfin:
                solara.Markdown(f"Title: {jf.media_item['Name']}")
                solara.Markdown(f"Position: {jf.position}")
                solara.Button(
                    "Play/Pause Jellyfin",
                    on_click=jf.play_pause,
                    classes=["button"],
                )
                solara.Button(
                    "Pause Jellyfin", on_click=jf.pause, classes=["button"]
                )
                solara.Button(
                    "Stop Jellyfin", on_click=jf.stop, classes=["button"]
                )
        solara.Button(
            "Play",
            on_click=local_load_item,
            disabled=(not jf.has_active_user_session) or is_video_id_playing_in_jellyfin,
            classes=["button"],
        )


    else:
        logger.debug("Jellyfin not connected/or no active")
        with solara.Column():
            solara.Image(pth, width="80px", classes=["mywarning", "pa-2"])
            # solara.Markdown("No active Jellyfin session found")


@solara.component
def SectionCounter(sections):
    solara.Markdown(f"Num Sections: {len(sections.value)}")


@solara.component
def SectionControlPanel(
    video,
    sections,
    current_section,
    create_section: callable = None,
    on_delete: callable = None,
):
    section_type = solara.use_reactive("intro")

    # existing sections
    num_sections = solara.use_reactive(len(sections.value))

    # text box for number of sections
    num_sections_input = solara.use_reactive(4)

    def delete_sections():
        for section in sections.value:
            on_delete(section)

    def clear_all_sections():
        delete_sections()
        sections.set([])

    def create_1_section():
        sm = SectionManager.from_video(video)
        new_sect_id = sm.create_section(start=0, end=video.duration, section_type=section_type.value)
        new_sect = SectionModel.get_by_id(new_sect_id)
        sections.set(sections.value + [new_sect])

    def split_into():
        # loading.set(False)
        if num_sections_input.value < 1:
            logger.error("Must have at least 1 section")
            return

        section_length = video.duration // num_sections_input.value
        if section_length < MIN_SECTION_LENGTH:
            logger.error(f"Sections must be at least {MIN_SECTION_LENGTH} seconds long")
            return
        elif section_length > MAX_SECTION_LENGTH:
            logger.error(
                f"Sections must be less than {MAX_SECTION_LENGTH} seconds long"
            )
            return
        num_new_sections = video.duration // section_length
        for i in range(num_new_sections):
            create_section(
                video=video,
                start=i * (video.duration / num_new_sections),
                end=(i + 1) * (video.duration / num_new_sections),
                section_type="instrumental",
            )

    with solara.Column():
        if num_sections.value > 0:
            solara.Markdown(
                f"Section ID {current_section.value.id if current_section is not None else "asdf"} selected ({num_sections.value } found)"
            )
            solara.Button(
                "Clear All Sections", on_click=clear_all_sections, classes=["button"]
            )
        else:
            solara.Button(
                "Single Section", on_click=create_1_section, classes=["button"]
            )
            with solara.Row():
                solara.InputInt("How Many Sections?", value=num_sections_input)
                solara.Button(
                    "Split",
                    on_click=split_into,
                    classes=["button"],
                )


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

@solara.component
def Page():
    MySidebar(router=solara.use_router())
    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    # jellyfin_logo = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")

    sm = SectionManager.from_video(video)
    reactive_sections = solara.use_reactive(sm.sections)
    # not sure why this is a tuple...
    section_dicts = (
        solara.use_reactive(
            [
                SectionManager.get_section_details(s.id)
                for s in reactive_sections.value
            ]
        ),
    )
    files = FileModel.select().where(FileModel.video_id == video.id)
    jf = MyJellyfinClient()

    def download_video(*args):
        logger.info(f"Downloading video: {video.title}")
        info, files = download_video_file(
            video.youtube_id, WORKING, progress_hook=my_hook
        )

        vid = VideoModel.select().where(VideoModel.id == video.id).get()
        for file in files:
            logger.debug(f"Processing files in download_video of the list item {file}")
            FileManager.add_path_to_video(file, vid)

    def create_album_nfo(*args):
        new_file = VideoItem.create_xml_for_jellyfin(video.id)
        FileManager.add_path_to_video(new_file, video)


    def create_section(*args, **kwargs):
        new_id = sm.create_section(
            start=0, end=video.duration, section_type="instrumental"
        )
        new_sect = SectionModel.get_by_id(new_id)
        reactive_sections.set(sm.sections + [new_sect])
        section_dicts.set(reactive_sections.value + [SectionManager.get_section_details(new_id)])
        logger.debug(f"New Section ID: {new_id}")

    def delete_section(*args):
        logger.debug(f"Deleting Section: {args}")
        delete_section_from_db(args[0]['section_id'])
        reactive_sections.set([s for s in reactive_sections.value if s.id != args[0]['section_id']])





    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))
    IMG_WIDTH = "300px"

    with solara.Column(classes=["main-container"]):
        with solara.Columns([6,3,3]):
            with solara.Column():
                solara.Image(image, width=IMG_WIDTH)
            with solara.Column():
                solara.Text(
                    f"{video.upload_date}",
                    classes=["medium-timer"],
                )
                solara.Text(
                    f"{seconds_to_hms(video.duration)}",
                    classes=["medium-timer"],
                )
                solara.Text(
                    f"{video.series.name if video.series else 'No Series'}",
                    classes=["medium-timer"],
                )
                solara.Text(
                    f"{video.youtube_series.title if video.youtube_series else 'No YT Series'}",
                    classes=["medium-timer"],
                )

            with solara.Column():
                NewJellyfinPanel(jf, video=video)
                FileTypeCheckboxes(
                    has_audio="audio" in [f.file_type for f in files],
                    has_video="video" in [f.file_type for f in files],
                    has_info="info" in [f.file_type for f in files],
                    has_subtitle="subtitle" in [f.file_type for f in files],
                    has_poster="poster" in [f.file_type for f in files],
                    has_album_nfo="album_nfo" in [f.file_type for f in files],
                    event_download_video=download_video,
                    event_create_album_nfo=create_album_nfo,
                    event_download_info=lambda x: logger.debug(
                        f"event_download_info {x}"
                    ),
                )




        SectionControlPanel(
            video=video,
            sections=reactive_sections,
            current_section=None,
            create_section=create_section,
            on_delete=lambda x: logger.debug(f"on_delete {x}"),
        )

        with solara.Row(classes=["mylight"]):
            if len(sm.sections) > 0:
                logger.debug(f"Num sections: {len(sm.sections)}")
                with solara.Columns([9,3]):
                # SectionCounter(sections=reactive_sections)
                    SectionTabs(
                    tabItems=section_dicts[0].value,
                    event_add_item=add_topic,
                    event_remove_item=remove_topic,
                    event_delete_section=delete_section,
                )
                    with solara.Card():
                        if video.album is not None:
                            poster = FileManager.get_file_for_album(video.album, "poster")
                            image = PIL.Image.open(Path(str(poster)))
                            solara.Image(image, width="200px")
                            solara.Text(f"{video.album.title}")
                        else:
                            solara.Markdown("No Album")
                            solara.Button("Add Album", classes=["button"])

            else:
                solara.Markdown("No Sections Found")
