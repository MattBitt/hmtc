import solara
from pathlib import Path
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
from hmtc.schemas.section import SectionManager
from hmtc.config import init_config
from loguru import logger
from hmtc.utils.youtube_functions import download_video_file


config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"


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
def SectionTabs(tabItems, event_add_item, event_remove_item):
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
    has_info: bool = True,
    has_poster: bool = True,
    event_download_video: callable = None,
    event_download_info: callable = None,
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


@solara.component
def Page():
    MySidebar(router=solara.use_router())
    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    # jellyfin_logo = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")

    model = solara.use_reactive(0)

    sm = SectionManager.from_video(video)
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

    def next_slide(*args):
        if model.value == len(sm.sections) - 1:
            model.set(0)
        else:
            model.set(model.value + 1)

    def prev_slide(*args):
        if model.value == 0:
            model.set(len(sm.sections) - 1)
        else:
            model.set(model.value - 1)

    poster = FileManager.get_file_for_video(video, "poster")
    image = PIL.Image.open(Path(str(poster)))
    IMG_WIDTH = "300px"
    with solara.Row(classes=["mylight"]):
        with solara.Columns([4, 4, 2, 2]):
            with solara.Column(classes=[""], style={"min_width": IMG_WIDTH}):
                solara.Image(image, width=IMG_WIDTH)
            with solara.Column(classes=[""]):
                solara.Text(
                    f"{video.upload_date}",
                    classes=["medium-timer"],
                )
                solara.Text(
                    f"{seconds_to_hms(video.duration)}",
                    classes=["medium-timer"],
                )

                SeriesChip(series=(video.series.name if video.series else "No Series"))
                if video.youtube_series and video.episode:
                    YoutubeSeriesChip(
                        youtube_series=(f"{video.youtube_series.title} {video.episode}")
                    )
                else:
                    YoutubeSeriesChip(youtube_series=("-----"))
            with solara.Column(classes=[""]):
                FileTypeCheckboxes(
                    has_audio="audio" in [f.file_type for f in files],
                    has_video="video" in [f.file_type for f in files],
                    has_info="info" in [f.file_type for f in files],
                    has_subtitle="subtitle" in [f.file_type for f in files],
                    has_poster="poster" in [f.file_type for f in files],
                    event_download_video=download_video,
                )

            if video.album is not None:
                poster = FileManager.get_file_for_album(video.album, "poster")
                image = PIL.Image.open(Path(str(poster)))
                solara.Image(image, width="200px")
                solara.Text(f"{video.album.title}")
            else:
                solara.Markdown("No Album")
                solara.Button("Add Album", classes=["button"])

    with solara.Row(classes=["mylight"]):
        if len(sm.sections) > 0:
            logger.debug(f"NUm sections: {len(sm.sections)}")

            section_dicts = [
                SectionManager.get_section_details(s.id) for s in sm.sections
            ]
            SectionTabs(
                tabItems=section_dicts,
                event_add_item=add_topic,
                event_remove_item=remove_topic,
            )

        else:
            solara.Markdown("No Sections Found")
