from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab import task
from solara.lab.toestand import Ref

from hmtc.schemas.playlist import PlaylistItem


@solara.component
def PlaylistEditModal(
    playlist_item: solara.Reactive[PlaylistItem],
    on_save: Callable[[], None],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    updating = solara.use_reactive(False)

    """Takes a reactive playlist item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(playlist_item.value)

    def save():
        playlist_item.value = copy.value
        on_save()

    def is_dirty():
        return playlist_item.value != copy.value

    def update_playlists():
        logger.debug(f"Updating playlist {playlist_item.value.name}")
        updating.set(True)
        playlist_item.value.db_object().check_for_new_playlists()
        updating.set(False)
        logger.success(f"Updated database from Playlist {playlist_item.value.name}")

    @task
    def update():
        logger.debug(f"Updating playlist {playlist_item.value.name}")
        updating.set(True)
        playlist_item.value.db_object().check_for_new_videos()
        updating.set(False)
        logger.success(f"Updated database from Playlist {playlist_item.value.name}")

    logger.debug("Start of PlaylistEdit")
    with solara.Card("Edit"):
        poster = playlist_item.value.db_object().poster
        if poster:
            solara.Image(poster, width="300px")
        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
        solara.InputText(label="Playlist Title", value=Ref(copy.fields.title))
        solara.InputText(label="URL", value=Ref(copy.fields.url))
        solara.InputText(label="YouTube ID", value=Ref(copy.fields.youtube_id))
        solara.Checkbox(label="Enabled", value=Ref(copy.fields.enabled))

        solara.Button(label="Check for new Videos", on_click=update)
        solara.Button(label="Check for new Playlists", on_click=update_playlists)

        with solara.CardActions():
            v.Spacer()
            solara.Button(
                "Save",
                icon_name="mdi-content-save",
                on_click=save,
                outlined=True,
                text=True,
                disabled=not is_dirty(),
            )
            solara.Button(
                "Close",
                icon_name="mdi-window-close",
                on_click=on_close,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Delete",
                icon_name="mdi-delete",
                on_click=on_delete,
                outlined=True,
                text=True,
            )
