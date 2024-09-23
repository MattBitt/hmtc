import solara
from pathlib import Path
from hmtc.components.shared.sidebar import MySidebar
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


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionTimeLine(
    whole_start=0,
    whole_end=2447,
    part_start=600,
    part_end=1200,
    section_number=0,
    total_sections=0,
    event_prev_slide: callable = None,
    event_next_slide: callable = None,
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
def Carousel(children=[], model=0):
    pass


@solara.component
def TopicsList():
    with solara.Row():
        solara.Markdown("Topics List")


@solara.component_vue("../components/section/section_topics.vue", vuetify=True)
def SectionTopics(
    topic: str,
    section_id: int,
    section_topics: list,
    event_add_topic: callable = None,
    event_remove_topic: callable = None,
):
    pass


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
    with solara.Row(classes=[""]):
        with solara.Columns([8, 4]):
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
                    YoutubeSeriesChip(youtube_series=(f"-----"))
            with solara.Column(classes=[""]):
                FileTypeCheckboxes(
                    has_audio="audio" in [f.file_type for f in files],
                    has_video="video" in [f.file_type for f in files],
                    has_info="info" in [f.file_type for f in files],
                    has_subtitle="subtitle" in [f.file_type for f in files],
                    has_poster="poster" in [f.file_type for f in files],
                    event_download_video=download_video,
                )

    with solara.Row(classes=["mylight"]):
        if video.album is not None:
            poster = FileManager.get_file_for_album(video.album, "poster")
            image = PIL.Image.open(Path(str(poster)))
            solara.Image(image, width="200px")
            solara.Text(f"{video.album.title}")
        else:
            solara.Markdown("No Album")
            solara.Button("Add Album", classes=["button"])

    if len(sm.sections) > 0:
        with solara.Row(classes=["mydark"]):
            SectionTimeLine(
                whole_start=0,
                whole_end=video.duration,
                part_start=sm.sections[model.value].start // 1000,
                part_end=sm.sections[model.value].end // 1000,
                section_number=model.value + 1,
                total_sections=len(sm.sections),
                event_prev_slide=prev_slide,
                event_next_slide=next_slide,
            )
        with solara.Row(classes=["myprimary"]):
            with Carousel(model=model.value):
                for section in sm.sections:

                    def add_topic(*args):
                        logger.debug(f"add_topic_and_add_to_section: {args}")
                        t, created = TopicModel.get_or_create(text=args[0])
                        if created:
                            logger.debug(f"Created topic {t.text}")
                        SectionTopicsModel.create(
                            section_id=section.id, topic_id=t.id, order=15
                        )

                    def remove_topic(*args):
                        logger.debug(f"remove_topic: {args} from seciton {section}")
                        t = (
                            TopicModel.select()
                            .where(TopicModel.text == args[0]["text"])
                            .get_or_none()
                        )
                        if t is None:
                            logger.error(f"Topic {args[0]} not found")
                            return

                        SectionTopicsModel.delete().where(
                            (SectionTopicsModel.section_id == section.id)
                            & (SectionTopicsModel.topic_id == t.id)
                        )
                        logger.error(
                            f"Removed topic {t.text} from section {section.id}"
                        )

                    with solara.Column():
                        solara.Text(f"id: {section.id}", classes=["ml-8 mt-4"])
                        st = (
                            TopicModel.select(TopicModel.id, TopicModel.text)
                            .join(SectionTopicsModel)
                            .where(SectionTopicsModel.section_id == section.id)
                            .order_by(SectionTopicsModel.order)
                        )

                        section_topics = [item.model_to_dict() for item in st]
                        logger.debug(
                            f"Section Topics: {section_topics} for section id {section.id}"
                        )
                        SectionTopics(
                            topic="",
                            section_id=section.id,
                            section_topics=section_topics,
                            event_add_topic=add_topic,
                            event_remove_topic=remove_topic,
                        )
                        SectionEditor(
                            item=section.model_to_dict(),
                        )

    else:
        solara.Markdown("No Sections Found")
