import solara

from hmtc.components.shared.dropdown import Dropdown
from hmtc.models import YoutubeSeries


@solara.component
def YoutubeSeriesDropdown(current_series, handle_click, color):
    serieses = YoutubeSeries.select().where(YoutubeSeries.title.is_null(False))
    items = [{"title": series.name, "id": series.id} for series in serieses]
    if current_series:
        caption = current_series["title"]
    else:
        caption = "All YoutubeSeries"
    Dropdown(
        items=items,
        caption=caption,
        handle_click=handle_click,
        color=color,
    )
