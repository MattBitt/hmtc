from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger

from hmtc.components.video.edit_modal import VideoEditModal
from hmtc.models import Video
from hmtc.schemas.video import VideoItem


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

    def update(*ignore_args):
        logger.error("Refresh button clicked and now updating")
        refreshing.value = True
        video_item.value = video_item.value.update_from_youtube()
        on_save(video_item.value)
        refreshing.value = False
        logger.error("Finished updating video item from youtube")

    with solara.Card():
        with solara.Column():
            if refreshing.value is True:
                solara.SpinnerSolara()
            else:
                solara.Markdown(f"### {video_item.value.title}")
                solara.InputText(f"ID: {video_item.value.id}", disabled=True)

                solara.Button(
                    "Edit Sections",
                    on_click=lambda: router.push(
                        f"/video-sections/{video_item.value.id}"
                    ),
                )
            with solara.Row():
                solara.Button(
                    icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
                )
                solara.Button(
                    icon_name="mdi-refresh",
                    icon=True,
                    on_click=update,
                    disabled=True,  # disabled in favor of the funtion in th modal
                ),

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
