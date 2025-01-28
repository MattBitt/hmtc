import solara
from loguru import logger

from hmtc.components.sectionalizer import Sectionalizer, Timeline
from hmtc.components.shared.ok_cancel import OkCancel
from hmtc.components.shared.sidebar import MySidebar
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.utils.subtitles import find_substantial_phrase_lines, read_vtt


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(router)

    with solara.Column(classes=["main-container"]):
        video = Video.get_by(id=1)
        Sectionalizer(video=video)
        captions = read_vtt(f"hmtc/utils/temp/omegle_50.en.vtt")
        starts = find_substantial_phrase_lines(
            captions, ["yeah", "yes", "yep", "ok", "okay"]
        )
        ends = find_substantial_phrase_lines(captions, ["let's go", "lets go"])
        solara.Markdown(f"Starts found: {starts}")
        solara.Markdown(f"Ends found: {ends}")
