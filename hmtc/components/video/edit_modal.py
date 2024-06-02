from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.schemas.video import VideoItem


@solara.component
def VideoEditModal(
    video_item: solara.Reactive[VideoItem],
    on_save: Callable[[], None],
    on_update: Callable[[], None],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    updating = solara.use_reactive(False)
    assert isinstance(video_item.value, VideoItem)

    copy = solara.use_reactive(video_item.value)

    def save():
        video_item.value = copy.value
        on_save()

    def update_from_youtube():
        on_update(video_item.value)

    def download_video():
        logger.info(f"Downloading video: {video_item.value.title}")

    def extract_audio():
        logger.info(f"Extracting Audio: {video_item.value.title}")

    def is_dirty():
        return video_item.value != copy.value

    with solara.Card("Edit"):
        poster = video_item.value.get_poster()

        if poster:
            solara.Image(poster, width="300px")

        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
        solara.InputText(label="Video Title", value=Ref(copy.fields.title))
        solara.InputText(label="URL", value=Ref(copy.fields.url))
        solara.InputText(label="YouTube ID", value=Ref(copy.fields.youtube_id))
        solara.InputText(label="Duration", value=Ref(copy.fields.duration))
        # solara.InputText(label="Upload Date", value=Ref(copy.fields.upload_date))
        solara.Checkbox(label="Enabled", value=Ref(copy.fields.enabled))
        solara.Checkbox(
            label="Contains Unique Content",
            value=Ref(copy.fields.contains_unique_content),
        )
        solara.Checkbox(label="Has Chapters", value=Ref(copy.fields.has_chapters))
        solara.Checkbox(label="Manually Edited", value=Ref(copy.fields.manually_edited))
        solara.InputText(label="Description", value=Ref(copy.fields.description))

        with solara.CardActions():
            v.Spacer()
            solara.Button(
                icon_name="mdi-refresh",
                icon=True,
                on_click=update_from_youtube,
            ),
            # mdi-video-box-off would be good if video is missing
            solara.Button(
                icon_name="mdi-movie-open",
                icon=True,
                on_click=download_video,
            )

            # mdi-speaker-off would be good if audio is missing
            solara.Button(
                icon_name="mdi-speaker",
                icon=True,
                on_click=extract_audio,
            )

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
