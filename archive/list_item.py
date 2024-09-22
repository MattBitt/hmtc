from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab import task

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
        max_width="90%",
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

    @task
    def download_video_info(*args, **kwargs):
        logger.debug("Not sure if this still works....")
        logger.debug(f"Downloading {playlist_item.value}")
        playlist_item.value.update_from_youtube()

    def update_videos():
        playlist_item.value.apply_to_videos()

    with solara.Card():
        with solara.Row():
            solara.Markdown(f"### {playlist_item.value.title}")
            solara.Markdown(f"#### ID:{playlist_item.value.id}")

        solara.Markdown(f"Num of Videos: {playlist_item.value.count_videos()}")
        solara.Markdown(
            f"Num of Videos (no duration): {playlist_item.value.count_videos(no_duration=True)}"
        )

        solara.InputText(f"URL: {playlist_item.value.url}", disabled=True)
        solara.InputText(f"Youtube ID: {playlist_item.value.youtube_id}", disabled=True)
        solara.Checkbox(label="Enabled", value=playlist_item.value.enabled)
        solara.Checkbox(
            label="Album per Episode", value=playlist_item.value.album_per_episode
        )
        solara.Checkbox(
            label="Enable Video Downloads",
            value=playlist_item.value.enable_video_downloads,
        )
        solara.Checkbox(label="Has Chapters", value=playlist_item.value.has_chapters)
        solara.Checkbox(
            label="Contains Unique Content",
            value=playlist_item.value.contains_unique_content,
        )

        with solara.CardActions():
            solara.Button(
                icon_name="mdi-pencil",
                icon=True,
                on_click=lambda: set_edit(True),
                disabled=True,
            )
            solara.Button(
                icon_name="mdi-download",
                icon=True,
                on_click=download_video_info,
                disabled=True,
            )
            solara.Button(
                icon_name="mdi-file-send",
                icon=True,
                on_click=update_videos,
            )
        if edit:
            logger.debug(f"Opening edit modal for {playlist_item.value}")
            open_modal(playlist_item, on_update, on_delete, edit, set_edit)
