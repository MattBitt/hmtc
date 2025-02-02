from functools import reduce

import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video as VideoModel


@solara.component
def Page():
    router = solara.use_router()
    videos = VideoModel.select().where(
        (VideoModel.duration > 0) & (VideoModel.unique_content == True)
    )
    recent = (
        VideoModel.select()
        .where((VideoModel.title.is_null(False)) & (VideoModel.unique_content == True))
        .order_by(VideoModel.upload_date.desc())
        .limit(10)
    )
    recent_updated = (
        VideoModel.select()
        .where(VideoModel.title.is_null(False) & (VideoModel.unique_content == True))
        .order_by(VideoModel.updated_at.desc())
        .limit(10)
    )

    seconds = reduce(lambda x, y: x + y.duration, videos, 0)
    days, hours, minutes, _seconds = (
        seconds // (24 * 3600),
        (seconds % (24 * 3600) // 3600),
        (seconds % 3600 // 60),
        (seconds % 60),
    )
    logger.debug(f"seconds: {seconds}")
    timestr = f"{days} days, {hours} hours, {minutes} minutes, {_seconds} seconds"
    with solara.Column(classes=["main-container"]):
        with solara.Card():
            with solara.Info():
                solara.Markdown("## Unique Content")
                solara.Markdown(f"### **{len(videos)}** videos")
                solara.Markdown(f"### Duration: **{timestr}**")
                solara.Markdown(f"### Duration (s): **{seconds}**")
        with solara.Card():
            solara.Markdown("## Recently Uploaded")
            for vid in recent:
                solara.Markdown(f"### -{vid.title} - {vid.upload_date}")
        with solara.Card():
            solara.Markdown("## Recently Updated")
            for vid in recent_updated:
                solara.Markdown(f"### -{vid.title} - {vid.updated_at}")
