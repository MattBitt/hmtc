import solara
from loguru import logger

from hmtc.models import Series


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def SeriesPopover(current_series, handle_click):
    logger.debug(f"SeriesPopover: {current_series}")
    serieses = None

    if current_series is None:
        caption = "All Series"
    else:
        caption = current_series["title"]

    query = Series.select()

    serieses = query.order_by(Series.name)

    items = [{"title": series.name, "id": series.id} for series in serieses]

    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
