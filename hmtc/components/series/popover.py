import solara
from loguru import logger

from hmtc.models import Series


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def SeriesPopover(current_series, handle_click, include_blank=False):
    logger.debug(f"SeriesPopover: {current_series}")
    serieses = None

    if include_blank and current_series == "NOSERIES":
        caption = "No Series"
    elif current_series is None:
        caption = "All Series"
    else:
        caption = current_series["title"]

    query = Series.select()
    if not include_blank:
        query = query.where(Series.name != "NOSERIES")

    serieses = query.order_by(Series.name)

    items = [{"title": series.name, "id": series.id} for series in serieses]
    if include_blank:
        items.append({"title": "NOSERIES", "id": None})

    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
