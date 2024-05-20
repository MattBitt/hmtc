from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger

from hmtc.components.video.edit_modal import VideoEditModal
from hmtc.schemas.video import VideoItem


def open_modal(
    item: solara.Reactive[VideoItem],
    on_update: Callable[[VideoItem], None],
    on_delete: Callable[[VideoItem], None],
    edit=None,
    set_edit=None,
):
    def on_delete_in_edit():
        on_delete(item.value)
        set_edit(False)

    def on_save_in_edit():
        logger.debug(f"on_save_in_edit: {item.value}")
        on_update(item.value)
        set_edit(False)

    with v.Dialog(
        v_model=edit,
        on_v_model=set_edit,
        persistent=True,
        max_width="80%",
    ):

        VideoEditModal(
            item,
            on_save=on_save_in_edit,
            on_delete=on_delete_in_edit,
            on_close=lambda: set_edit(False),
        )


@solara.component
def VideoListItem(
    video_item: solara.Reactive[VideoItem],
    on_update: Callable[[VideoItem], None],
    on_delete: Callable[[VideoItem], None],
):
    edit, set_edit = solara.use_state(False)
    refreshing = solara.use_reactive(False)

    def update():
        refreshing.value = True
        video_item.value.update_from_youtube()
        refreshing.value = False

    with solara.Card():
        with solara.Column():
            if refreshing.value:
                solara.SpinnerSolara()
            else:
                solara.Markdown(f"### {video_item.value.title}")
                solara.InputText(f"ID: {video_item.value.id}", disabled=True)
            with solara.Row():
                solara.Button(
                    icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
                )
                solara.Button(
                    icon_name="mdi-refresh",
                    icon=True,
                    on_click=update,
                ),

            if edit:
                logger.debug(f"Opening edit modal for {video_item.value}")
                open_modal(video_item, on_update, on_delete, edit, set_edit)
