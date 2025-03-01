import solara
import solara.lab
from loguru import logger

from hmtc.components.shared import Chip, InputAndDisplay, MySpinner
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.video import Video
from hmtc.models import Video as VideoModel


@solara.component
def Sandbox():
    vid = VideoModel.select().where(VideoModel.unique_content == True).first()
    video = Video(vid.id)
    JFPanel(video)
    solara.Markdown(f"Sandbox Page.")
