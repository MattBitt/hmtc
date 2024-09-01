from pathlib import Path
from typing import Callable
import reacton.ipyvuetify as v
import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.video.edit_modal import VideoEditModal
from hmtc.components.video.series_popover import VideoSeriesPopover
from hmtc.config import init_config
from hmtc.models import Video
from hmtc.mods.file import FileManager
from hmtc.schemas.video import VideoItem
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"

current_download_progress = solara.reactive(0)


def duration_text(duration):
    hours, minutes, seconds = (
        (duration % (24 * 3600) // 3600),
        (duration % 3600 // 60),
        (duration % 60),
    )
    if hours > 0:
        timestr = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    else:
        timestr = f"{minutes} minutes, {seconds} seconds"

    # logger.debug(f"timestr: {timestr}")
    return timestr


def my_hook(*args):
    # this seems to work but not getting the feedback on the page
    pass
    # d = args[0]["downloaded_bytes"]
    # t = args[0]["total_bytes"]
    # p = d / t * 100
    # if p < 1:
    #     logger.info(f"Percent Complete: {d/t*100:.2f}%")
    # current_download_progress.set(p)


def download_video(video_item):
    logger.info(f"Downloading video: {video_item.value.title}")
    info, files = download_video_file(
        video_item.value.youtube_id, WORKING, progress_hook=my_hook
    )

    vid = Video.select().where(Video.id == video_item.value.id).get()
    for file in files:
        logger.debug(f"Processing files in download_video of the list item {file}")
        FileManager.add_path_to_video(file, vid)


def extract(video_item, *ignore_args):
    logger.error("Extracting frames")
    frames = video_item.value.extract_frames()
    logger.error("Frames extracted")

    for frame in frames:
        video_item.value.add_frame(frame)


def update(refreshing, video_item, on_save, *ignore_args):
    logger.error("Refresh button clicked and now updating")

    refreshing.value = True

    video_item.value.update_from_youtube()

    on_save(video_item.value)
    refreshing.value = False

    logger.error("Finished updating video item from youtube")


@solara.component
def ToolTipButton(icon_name, on_click, tooltip, color=None, disabled=None):
    with solara.Tooltip(tooltip):
        solara.Button(
            icon_name=icon_name,
            icon=True,
            on_click=on_click,
            color=color,
            disabled=disabled,
        )


@solara.component
def FileToolTipButton(
    icon_name, on_click, tooltip, color=None, disabled=None, file_type=None
):
    with solara.Tooltip(tooltip):
        solara.Button(
            icon_name=icon_name,
            icon=True,
            on_click=on_click,
            color=color,
            disabled=disabled,
        )


def open_modal(
    item: solara.Reactive[VideoItem],
    on_save: Callable[[VideoItem], None],
    on_update_from_youtube: Callable[[VideoItem], None],
    on_delete: Callable[[VideoItem], None],
    edit=None,
    set_edit=None,
):
    def on_delete_in_edit():
        on_delete(item.value)
        set_edit(False)

    def on_save_in_edit():
        logger.debug(f"on_save_in_edit: {item.value}")
        on_save(item.value)
        set_edit(False)

    def on_update_in_edit(item):
        logger.debug(f"on_update_in_edit: {item.title}")
        on_update_from_youtube(item)
        set_edit(False)

    with v.Dialog(
        v_model=edit,
        on_v_model=set_edit,
        persistent=True,
        max_width="80%",
    ):
        assert isinstance(item.value, VideoItem)
        VideoEditModal(
            item,
            on_save=on_save_in_edit,
            on_delete=on_delete_in_edit,
            on_update=on_update_in_edit,
            on_close=lambda: set_edit(False),
        )


@solara.component
def ActionsToolBar(
    video_item: solara.Reactive[VideoItem],
    router,
    set_edit,
    has_info=False,
    justify="center",
):
    color = "5b7a8e"
    with solara.Row(justify=justify):
        ToolTipButton(
            icon_name="mdi-pencil",
            on_click=lambda: set_edit(True),
            tooltip="Edit Video",
            color=color,
            disabled=False,
        )

        ToolTipButton(
            icon_name="mdi-rhombus-split",
            on_click=lambda: router.push(f"/video-sections/{video_item.value.id}"),
            tooltip="Edit Sections",
            color=color,
            disabled=not has_info,
        )

        ToolTipButton(
            icon_name="mdi-album",
            on_click=lambda: router.push(f"/video-album/{video_item.value.id}"),
            tooltip="Edit Album",
            color=color,
            disabled=not has_info,
        )


@solara.component
def FilesToolbar(
    video_item: solara.Reactive[VideoItem],
    refreshing: solara.Reactive[bool],
    router,
    has_info=False,
    has_video=False,
    has_frames=False,
    has_audio=False,
    has_poster=False,
    justify="center",
    refresh_query=None,
):
    def dwnld():
        logger.error("Downloading video")
        refreshing.set(True)
        current_download_progress.set(0)
        download_video(video_item)
        refreshing.set(False)
        refresh_query()

    def updt():
        logger.error("Updating video")
        refreshing.set(True)
        video_item.value.update_from_youtube()
        refreshing.set(False)
        refresh_query()

    color = "FFA500"

    with solara.Row(justify=justify):
        ToolTipButton(
            icon_name="mdi-information",
            on_click=updt,
            tooltip="Download Info from Youtube",
            color=str(Colors.PRIMARY),
            disabled=has_info,
        )

        ToolTipButton(
            icon_name="mdi-movie",
            on_click=dwnld,
            tooltip="Download Video from YouTube",
            color=str(Colors.DARK),
            disabled=has_video or not has_info,
        )

        ToolTipButton(
            icon_name="mdi-speaker",
            on_click=lambda: logger.error("Extracting audio"),
            color=str(Colors.DARK),
            tooltip="Create Audio File",
            disabled=(not has_video or has_audio) or not has_info,
        )

        ToolTipButton(
            icon_name="mdi-note-text",
            on_click=lambda: logger.error("Extracting subtitles"),
            tooltip="Download Info JSON",
            color=str(Colors.DARK),
            disabled=has_video or not has_info,
        )

        ToolTipButton(
            icon_name="mdi-image",
            on_click=lambda: logger.error("Extracting poster"),
            color=str(Colors.DARK),
            tooltip="Download Poster",
            disabled=has_poster or not has_info,
        )
        ToolTipButton(
            icon_name="mdi-focus-field",
            on_click=extract,
            color=str(Colors.DARK),
            tooltip="Extract Image Frames",
            disabled=(not has_video or has_frames),
        )


@solara.component
def VideoListItem(
    video_item: solara.Reactive[VideoItem],
    refreshing: solara.Reactive[bool],
    router,
    on_save: Callable[[VideoItem], None],
    refresh_query: Callable[[VideoItem], None],
    on_delete: Callable[[VideoItem], None],
):
    edit, set_edit = solara.use_state(False)
    # current_series = solara.use_reactive(video_item.value.series_name)
    if video_item.value is None:
        logger.error("No video item to display")
        return

    def on_click_series(*args):
        if args[0]:
            logger.debug(args[0])
            video_item.value.update_series(args[0]["title"])
            refresh_query()
        else:
            logger.debug(f"No args[0] in on_click_series {args}")

    if refreshing.value is True:
        with solara.Column():
            solara.SpinnerSolara()
            solara.Info(f"Refreshing {video_item.value.title}")
            solara.Info(f"Progress: {current_download_progress.value:.2f}%")

    elif video_item.value.duration is None:
        with solara.Column():

            solara.Error("Please update video information from YouTube")
            has_info = False
            has_video = False
            has_frames = False
            has_audio = False
            has_poster = False
    else:
        p = FileManager.get_file_for_video(video_item.value, "poster")
        if p:
            poster = Path(str(p))
            if poster is not None and poster != "":
                # logger.debug(f"Poster = {poster}")
                has_poster = True
                # image = PIL.Image.open(poster)
                # solara.Image(image, width="200px")

        else:
            has_poster = False
        has_info = True
        has_video = VideoItem.has_video_file(id=video_item.value.id)
        has_frames = VideoItem.has_frame_files(id=video_item.value.id)
        has_audio = False  # VideoItem.has_audio_file(id=video_item.value.id)

        with solara.Column():
            if video_item.value.title is None:
                with solara.Error():
                    solara.Text("No Title")
                    logger.error("No Title found for video")
                    return

            if video_item.value.contains_unique_content:

                with solara.Success():
                    solara.Text(f"## {video_item.value.title[:80]}")
                    if video_item.value.episode and video_item.value.youtube_series:
                        solara.Markdown(
                            f"#### {video_item.value.youtube_series.title} {video_item.value.episode}"
                        )

            else:
                with solara.Error():
                    solara.Text(f"{video_item.value.title[:80]}")

            with solara.Columns(1, 1, 1):
                solara.Text(f"ID: {video_item.value.id}", classes=["mizzle"])
                solara.Text(
                    f"{duration_text(video_item.value.duration)}",
                    classes=["mizzle"],
                )
                solara.Text(f"{video_item.value.upload_date}", classes=["mizzle"])

            with solara.Row():
                VideoSeriesPopover(
                    current_series=video_item.value.series.name,
                    handle_click=on_click_series,
                )
                solara.Text(
                    f"Channel: {video_item.value.channel.name}",
                    classes=["mizzle"],
                )
                if video_item.value.youtube_series:
                    solara.Text(
                        f"Youtube Series: {video_item.value.youtube_series.title}",
                        classes=["mizzle"],
                    )

        with solara.Columns(6, 6):
            FilesToolbar(
                video_item=video_item,
                router=router,
                has_info=has_info,
                has_video=has_video,
                has_frames=has_frames,
                has_audio=has_audio,
                has_poster=has_poster,
                refreshing=refreshing,
                justify="start",
                refresh_query=refresh_query,
            )

            ActionsToolBar(
                video_item=video_item,
                router=router,
                has_info=has_info,
                set_edit=set_edit,
                justify="end",
            )

        if edit:
            logger.debug(f"Opening edit modal for {video_item.value.title}")
            if isinstance(video_item.value, Video):
                logger.error(
                    "If this doesn't show up in the logs, delete this code 8-21-24 🥦🥦🥦🥦"
                )
                video_item.value = VideoItem.from_orm(video_item.value)

            open_modal(
                item=video_item,
                on_save=on_save,
                on_update_from_youtube=None,
                on_delete=on_delete,
                edit=edit,
                set_edit=set_edit,
            )
