import solara
from loguru import logger
from functools import reduce
from hmtc.components.shared.sidebar import MySidebar, State as SidebarState
from hmtc.models import Video


@solara.component
def Page():
    router = solara.use_router()
    videos = Video.select().where(Video.duration > 0)
    logger.debug(f"videos: {len(videos)}")
    MySidebar(
        router=router,
    )
    seconds = reduce(lambda x, y: x + y.duration, videos, 0)
    days, hours, minutes, seconds = (
        seconds // (24 * 3600),
        (seconds % (24 * 3600) // 3600),
        (seconds % 3600 // 60),
        (seconds % 60),
    )
    logger.debug(f"seconds: {seconds}")
    timestr = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    solara.Markdown(f"Total duration (known)")
    solara.Markdown(f"## {timestr}")
