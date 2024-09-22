import solara

from hmtc.components.shared.dropdown import Dropdown
from hmtc.models import Series


@solara.component
def SeriesDropdown(current_series, handle_click, color):
    serieses = Series.select().where(Series.name.is_null(False))
    items = [{"title": series.name, "id": series.id} for series in serieses]
    if current_series:
        caption = current_series["title"]
    else:
        caption = "All Series"
    Dropdown(
        items=items,
        caption=caption,
        handle_click=handle_click,
        color=color,
    )
