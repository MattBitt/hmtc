import solara
from loguru import logger

from hmtc.components.shared.ok_cancel import OkCancel
from hmtc.components.shared.sidebar import MySidebar
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import ChannelFile as ChannelFileModel


@solara.component
def Page():
    router = solara.use_router()
    logger.error(f"router: {router.parts}")
    MySidebar(router)

    def func1(*args):
        logger.debug("OK from the main page!!!!")

    def func2(*args):
        logger.debug("CANCEL from the main page!!!!")

    with solara.Column(classes=["main-container"]):
        OkCancel(message="Are you sure?", func_ok=func1, func_cancel=func2)
        video = Video.get_by(
            title="Strangers Fall In Love With Harry Mack's Freestyles On Omegle | Omegle Bars Ep. 1"
        )

        # solara.Image(image=video.poster, width="300px")
        for channel in Channel.repo.all():
            _channel = Channel(channel)
            solara.Image(image=_channel.poster, width="300px")
