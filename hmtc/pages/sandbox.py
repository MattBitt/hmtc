import ipyvue
import solara
from loguru import logger
from peewee import fn
from hmtc.components.shared.sidebar import MySidebar
from hmtc.schemas.video import VideoItem


@solara.component_vue("sandbox.vue")
def Sandbox():
    pass


@solara.component
def Page():

    MySidebar(router=solara.use_router())
    Sandbox()
    x = VideoItem.video_file_counts(unique=True)
    solara.Markdown(f"Total number of unique video files: {x['video_files']}")
    solara.Markdown(f"Total number of unique audio files: {x['audio_files']}")
