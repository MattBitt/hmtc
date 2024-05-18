from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.playlist.playlist_edit_modal import PlaylistEditModal
from hmtc.schemas.playlist import PlaylistItem


@solara.component
def PlaylistListItem(
    playlist_item: solara.Reactive[PlaylistItem],
    on_update: Callable[[PlaylistItem], None],
    on_delete: Callable[[PlaylistItem], None],
):
    """Displays a single playlist item, modifications are done 'in place'.

    For demonstration purposes, we allow editing the item in a dialog as well.
    This will not modify the original item until 'save' is clicked.
    """
    edit, set_edit = solara.use_state(False)
    with solara.Card():
        with v.ListItem():
            solara.InputText(
                label="", value=Ref(playlist_item.fields.title), disabled=True
            )
            solara.InputText(f"ID: {playlist_item.value.id}", disabled=True)

            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )

            with v.Dialog(
                v_model=edit, persistent=True, max_width="80%", on_v_model=set_edit
            ):
                if edit:  # 'reset' the component state on open/close

                    def on_delete_in_edit():
                        on_delete(playlist_item.value)
                        set_edit(False)

                    def on_save_in_edit():
                        logger.debug(f"on_save_in_edit: {playlist_item.value}")
                        on_update(playlist_item.value)
                        set_edit(False)

                    PlaylistEditModal(
                        playlist_item,
                        on_save=on_save_in_edit,
                        on_delete=on_delete_in_edit,
                        on_close=lambda: set_edit(False),
                    )
