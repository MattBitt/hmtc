from functools import reduce

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video


@solara.component
def Page():
    router = solara.use_router()
    videos = Video.select().where(
        (Video.duration > 0) & (Video.contains_unique_content is True)
    )
    recent = (
        Video.select()
        .where((Video.title.is_null(False)) & (Video.contains_unique_content is True))
        .order_by(Video.upload_date.desc())
        .limit(10)
    )
    recent_updated = (
        Video.select()
        .where(Video.title.is_null(False) & (Video.contains_unique_content is True))
        .order_by(Video.updated_at.desc())
        .limit(10)
    )

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
    with solara.Column(classes=["main-container"]):
        with solara.Info():
            solara.Markdown("## Unique Content")
            solara.Markdown(f"### **{len(videos)}** videos")
            solara.Markdown(f"### Duration: **{timestr}**")
        with solara.Card():
            solara.Markdown("## Recently Uploaded")
            for vid in recent:
                solara.Markdown(f"### -{vid.title} - {vid.upload_date}")
        with solara.Card():
            solara.Markdown("## Recently Updated")
            for vid in recent_updated:
                solara.Markdown(f"### -{vid.title} - {vid.updated_at}")
