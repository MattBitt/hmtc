from pathlib import Path
from typing import Callable

import reacton.ipyvuetify as v
import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.config import init_config
from hmtc.schemas.video import VideoItem
from hmtc.utils.youtube_functions import download_video_file
from hmtc.mods.file import FileManager
import PIL.Image

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


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
        # on_update(video_item.value)
        pass

    def download_video():
        pass
        # logger.info(f"Downloading video: {video_item.value.title}")
        # ##info, files = download_media_files(video_item.value.youtube_id, WORKING)
        # ###for file in files:
        #     video_item.value.add_file(file)

    def extract_audio():
        pass
        # logger.debug(f"Fake Audio Extraction {video_item.value.title}")

    def is_dirty():
        return video_item.value != copy.value

    with solara.Card("Edit"):

        poster = Path(str(FileManager.get_file_for_video(video_item.value, "poster")))
        if poster is not None and poster != "":
            logger.debug(f"Poster = {poster}")
            has_poster = True
            image = PIL.Image.open(poster)
            solara.Image(image, width="300px")

        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
        solara.InputText(label="Video Title", value=Ref(copy.fields.title))
        solara.InputText(label="URL", value=Ref(copy.fields.url))
        solara.InputText(label="YouTube ID", value=Ref(copy.fields.youtube_id))
        solara.InputText(label="Duration", value=Ref(copy.fields.duration))
        solara.InputText(label="Channel", value=Ref(copy.fields.channel_id))
        solara.InputText(label="Series", value=Ref(copy.fields.series_id))
        solara.InputText(label="Playlist", value=Ref(copy.fields.playlist_id))
        solara.InputText(label="Episode", value=Ref(copy.fields.episode))

        # solara.InputText(label="Upload Date", value=Ref(copy.fields.upload_date))
        with solara.Row():
            solara.Checkbox(label="Enabled", value=Ref(copy.fields.enabled))
            solara.Checkbox(
                label="Unique",
                value=Ref(copy.fields.contains_unique_content),
            )
            solara.Checkbox(label="Has Chapters", value=Ref(copy.fields.has_chapters))
            solara.Checkbox(
                label="Manually Edited", value=Ref(copy.fields.manually_edited)
            )
        solara.InputText(label="Description", value=Ref(copy.fields.description))

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
