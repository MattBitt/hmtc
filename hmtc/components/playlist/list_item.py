from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger

from hmtc.components.playlist.edit_modal import PlaylistEditModal
from hmtc.schemas.playlist import PlaylistItem


def open_modal(
    item: solara.Reactive[PlaylistItem],
    on_update: Callable[[PlaylistItem], None],
    on_delete: Callable[[PlaylistItem], None],
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

        PlaylistEditModal(
            item,
            on_save=on_save_in_edit,
            on_delete=on_delete_in_edit,
            on_close=lambda: set_edit(False),
        )


@solara.component
def PlaylistListItem(
    playlist_item: solara.Reactive[PlaylistItem],
    on_update: Callable[[PlaylistItem], None],
    on_delete: Callable[[PlaylistItem], None],
):
    edit, set_edit = solara.use_state(False)
    with solara.Card():
        with solara.Column():
            solara.Markdown(f"### {playlist_item.value.title}")
            solara.Markdown(f"Num of Videos: {playlist_item.value.count_videos()}")
            solara.InputText(f"ID: {playlist_item.value.id}", disabled=True)
            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )
            if edit:
                logger.debug(f"Opening edit modal for {playlist_item.value}")
                open_modal(playlist_item, on_update, on_delete, edit, set_edit)
