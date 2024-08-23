import solara
from loguru import logger

from hmtc.models import YoutubeSeries


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def YoutubeSeriesPopover(current_youtube_series, handle_click):
    logger.debug(f"YoutubeSeriesPopover: {current_youtube_series}")
    serieses = None

    if current_youtube_series is None:
        caption = "All YoutubeSeries"
    else:
        caption = current_youtube_series["title"]

    query = YoutubeSeries.select()

    serieses = query.order_by(YoutubeSeries.title)

    items = [{"title": series.title, "id": series.id} for series in serieses]

    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
