import solara

from hmtc.models import Series


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def VideoSeriesPopover(current_series, handle_click):
    # def on_click(*args):
    #     logger.error(f"local on click for testing 🟣🟣🟣🟣 {args}")

    caption = current_series if current_series else "-------"
    serieses = Series.select().order_by(Series.name)
    items = [{"title": series.name, "id": series.id} for series in serieses]

    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
