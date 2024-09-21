import solara
from pathlib import Path
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.video import VideoItem
from hmtc.schemas.file import FileManager
import PIL
from hmtc.models import Video as VideoModel, Section, File as FileModel
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


@solara.component_vue("../components/file/file_type_checkboxes.vue", vuetify=True)
def FileTypeCheckboxes(
    has_audio: bool,
    has_video: bool,
    has_subtitle: bool,
    has_info: bool,
    has_poster: bool,
    event_download_video: callable,
):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionTimeLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    ),
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
def Page():
    MySidebar(router=solara.use_router())
    video_id = parse_url_args()
    video = VideoItem.get_details_for_video(video_id)
    jellyfin_logo = Path("./hmtc/assets/icons/jellyfin.1024x1023.png")

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

    def next_slide():
        if model.value == len(sm.sections) - 1:
            model.set(0)
        else:
            model.set(model.value + 1)

    def prev_slide():
        if model.value == 0:
            model.set(len(sm.sections) - 1)
        else:
            model.set(model.value - 1)

    with solara.Column(classes=["main-container"]):
        with solara.Row(style={"background-color": "lightgrey"}):
            with solara.ColumnsResponsive(12, large=[6, 3, 3]):
                with solara.Card():
                    with solara.Columns([4, 4, 4]):

                        with solara.Column():
                            poster = FileManager.get_file_for_video(video, "poster")
                            image = PIL.Image.open(Path(str(poster)))
                            solara.Image(image, width="200px")

                            solara.Text(
                                f"{video.upload_date}",
                                classes=["medium-timer"],
                            )
                            solara.Text(
                                f"{seconds_to_hms(video.duration)}",
                                classes=["medium-timer"],
                            )
                        with solara.Column(align="start"):
                            SeriesChip(
                                series=(
                                    video.series.name if video.series else "No Series"
                                )
                            )

                            AlbumChip(
                                album=(video.album.title if video.album else "No Album")
                            )
                            YoutubeSeriesChip(
                                youtube_series=(
                                    video.youtube_series.title
                                    if video.youtube_series
                                    else "No Youtube Series"
                                )
                            )
                            ChannelChip(
                                channel=(
                                    video.channel.name
                                    if video.channel
                                    else "No Channel"
                                )
                            )
                            PlaylistChip(
                                playlist=(
                                    video.playlist.title
                                    if video.playlist
                                    else "No Playlist"
                                )
                            )

                        with solara.Column(align="center"):
                            FileTypeCheckboxes(
                                has_audio="audio" in [f.file_type for f in files],
                                has_video="video" in [f.file_type for f in files],
                                has_info="info" in [f.file_type for f in files],
                                has_subtitle="subtitle" in [f.file_type for f in files],
                                has_poster="poster" in [f.file_type for f in files],
                                event_download_video=download_video,
                            )
                            if "video" not in [f.file_type for f in files]:
                                solara.Button(
                                    "Download Video",
                                    classes=["button"],
                                    on_click=download_video,
                                )
                with solara.Card():
                    with solara.Column():
                        if video.album is not None:
                            poster = FileManager.get_file_for_album(
                                video.album, "poster"
                            )
                            image = PIL.Image.open(Path(str(poster)))
                            solara.Image(image, width="200px")
                            solara.Text(f"{video.album.title}")
                        else:
                            solara.Markdown("No Album")
                            solara.Button("Add Album", classes=["button"])

                with solara.Card():
                    with solara.Columns([2, 10]):
                        solara.Image(jellyfin_logo, width="50px")
                        with solara.Column():
                            solara.Markdown(f"###### Jellyfin Status")
                            solara.Markdown(f"* Jellyfin Status")
                            solara.Markdown(f"* asdf Status")
                            solara.Markdown(f"* Status of the fin made of jelly")
        with solara.Row(style={"background-color": "lightgrey"}):
            with solara.ColumnsResponsive(12):
                with solara.Card():

                    # SectionListItem(
                    #     items=[sect.model_to_dict() for sect in sm.sections],
                    # )

                    with solara.Column():
                        with solara.Row(justify="space-between"):
                            solara.Button(
                                "Previous", on_click=prev_slide, classes=["button"]
                            )
                            solara.Markdown(
                                f"## Section {model.value + 1} of {len(sm.sections)}"
                            )
                            solara.Button(
                                "Next", on_click=next_slide, classes=["button"]
                            )
                        with solara.Column():
                            if len(sm.sections) > 0:
                                SectionTimeLine(
                                    timestamps=dict(
                                        whole_start=0,
                                        whole_end=video.duration,
                                        part_start=sm.sections[model.value].start
                                        // 1000,
                                        part_end=sm.sections[model.value].end // 1000,
                                    )
                                )
                            else:
                                solara.Markdown("No Sections Found")

                        with Carousel(model=model.value):
                            for section in sm.sections:
                                s = solara.use_reactive(section)
                                with solara.Column():
                                    solara.Text(f"s.value = {s.value}")
                                    solara.Text(f"Start: {section.start}")
                                    solara.Text(f"End: {section.end}")
        with solara.Row(style={"background-color": "lightgrey"}):
            with solara.ColumnsResponsive(12, large=6):

                with solara.Card():
                    solara.Markdown(f"###### ?? Info")
                    solara.Markdown(f"* {video.duration}")
