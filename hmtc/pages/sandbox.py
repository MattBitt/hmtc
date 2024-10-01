import ipyvue
import solara
from loguru import logger
from peewee import fn
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel
from hmtc.models import File as FileModel


@solara.component_vue("sandbox.vue")
def Sandbox():
    pass


@solara.component
def Page():

    MySidebar(router=solara.use_router())
    vids_with_video = FileModel.select(FileModel.id, FileModel.video_id).where(
        (FileModel.video_id.is_null(False)) & (FileModel.file_type == "video")
    )
    vids_with_audio = FileModel.select(FileModel.id, FileModel.video_id).where(
        (FileModel.video_id.is_null(False) & (FileModel.file_type == "audio"))
    )
    x = [v.video_id for v in vids_with_video]
    y = [v.video_id for v in vids_with_audio]
    missing_audio = [v for v in x if v not in y]
    solara.Markdown(f"## xx{len(vids_with_video)} Videos have video files")
    solara.Markdown(f"## xx{len(vids_with_audio)} Videos have audio files")
    for vid in missing_audio:
        v = VideoModel.get(VideoModel.id == vid)
        solara.Markdown(f"## {vid} is missing audio")
