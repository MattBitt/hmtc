import solara
from loguru import logger

from hmtc.components.sectionalizer import Sectionalizer, Timeline
from hmtc.components.shared.ok_cancel import OkCancel
from hmtc.components.shared.sidebar import MySidebar
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(router)

    with solara.Column(classes=["main-container"]):
        video = Video.get_by(id=1)
        Sectionalizer(video=video)
