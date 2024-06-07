import solara

from hmtc.models import Series


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def SeriesPopover(current_series, handle_click):
    serieses = Series.select().where(Series.name.is_null(False)).order_by(Series.name)
    items = [{"title": series.name, "id": series.id} for series in serieses]
    if current_series:
        caption = current_series["title"]
    else:
        caption = "All Series"
    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
