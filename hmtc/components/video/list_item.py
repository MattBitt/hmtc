from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger

from hmtc.components.video.edit_modal import VideoEditModal
from hmtc.models import Video
from hmtc.schemas.video import VideoItem
from hmtc.utils.youtube_functions import download_media_files
from hmtc.config import init_config
from pathlib import Path

config = init_config()
WORKING = Path(config["paths"]["working"]) / "downloads"
STORAGE = Path(config["paths"]["storage"]) / "videos"


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
def VideoListItem(
    video_item: solara.Reactive[VideoItem],
    router,
    on_save: Callable[[VideoItem], None],
    on_update_from_youtube: Callable[[VideoItem], None],
    on_delete: Callable[[VideoItem], None],
):
    edit, set_edit = solara.use_state(False)
    refreshing = solara.use_reactive(False)

    def download_video():
        logger.info(f"Downloading video: {video_item.value.title}")
        info, files = download_media_files(video_item.value.youtube_id, WORKING)
        for file in files:
            video_item.value.add_file(file)

    def extract(*ignore_args):
        logger.error("Extracting frames")
        frames = video_item.value.extract_frames()
        logger.error("Frames extracted")

        for frame in frames:
            video_item.value.add_frame(frame)

    def update(*ignore_args):
        logger.error("Refresh button clicked and now updating")
        refreshing.value = True
        video_item.value.update_from_youtube()
        on_save(video_item.value)
        refreshing.value = False
        logger.error("Finished updating video item from youtube")

    with solara.Card():
        has_info = video_item.value.duration is not None
        has_video = VideoItem.has_video_file(id=video_item.value.id)
        has_frames = VideoItem.has_frame_files(id=video_item.value.id)
        if has_frames:
            color = "blue"
        else:
            color = "red"
        if has_video:
            try:
                vf = VideoItem.get_video_file_path(id=video_item.value.id)[0]
            except IndexError as e:
                logger.error(e)
                raise e

        with solara.Column():
            if refreshing.value is True:
                solara.SpinnerSolara()
            else:
                solara.Markdown(f"### {video_item.value.title}")
                solara.InputText(f"ID: {video_item.value.id}", disabled=True)
                solara.Markdown(f"Series: {video_item.value.series_name}")
                solara.Markdown(f"Playlist: {video_item.value.playlist_name}")
                solara.Button(
                    "Edit Sections",
                    on_click=lambda: router.push(
                        f"/video-sections/{video_item.value.id}"
                    ),
                )
                if has_video:
                    solara.Markdown(f"Video path = {vf.file_string}")
            with solara.Row():
                with solara.Tooltip("Edit Video Info"):
                    solara.Button(
                        icon_name="mdi-pencil",
                        icon=True,
                        on_click=lambda: set_edit(True),
                    )
                with solara.Tooltip("Update from Youtube"):
                    solara.Button(
                        color=color,
                        icon_name="mdi-information",
                        icon=True,
                        on_click=update,
                        disabled=has_info,
                    ),
                with solara.Tooltip("Download Video from YouTube"):
                    solara.Button(
                        color=color,
                        icon_name="mdi-movie",
                        icon=True,
                        on_click=download_video,
                        disabled=has_video,
                    )
                with solara.Tooltip("Extract Frames from Video"):
                    solara.Button(
                        color=color,
                        icon_name="mdi-focus-field",
                        icon=True,
                        on_click=extract,
                        disabled=(not has_video or has_frames),
                    )

            if edit:
                logger.debug(f"Opening edit modal for {video_item.value.title}")
                if isinstance(video_item.value, Video):
                    video_item.value = VideoItem.from_orm(video_item.value)
                assert isinstance(video_item.value, VideoItem)
                open_modal(
                    item=video_item,
                    on_save=on_save,
                    on_update_from_youtube=update,
                    on_delete=on_delete,
                    edit=edit,
                    set_edit=set_edit,
                )
