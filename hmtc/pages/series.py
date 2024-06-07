import peewee
import solara
import solara.lab
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Series, Video

name = solara.reactive("")
start_date = solara.reactive("2001-01-01")
end_date = solara.reactive("2024-12-31")


def videos_by_series(series):
    return Video.select().where((Video.series == series) & (Video.enabled == True))


def add_series():
    logger.debug("About to add series")
    try:
        Series.create(name="New Series", start_date="2021-01-01", end_date="2024-12-31")
    except peewee.IntegrityError:
        logger.error("Series already exists")
        return


@solara.component
def SeriesForm():
    with solara.Card():
        solara.InputText("Series Name", value=name)
        solara.InputText("Series Start Date", value=start_date)
        solara.InputText("Series End Date", value=end_date)
        solara.Button("Submit", on_click=add_series)


@solara.component
def SeriesCard(series):
    with solara.Card():
        solara.Markdown(f"# {series.name}")
        if series.poster is not None:
            solara.Image(series.poster, width="400px")
        solara.Markdown(f"* {series.unique_videos} unique source videos")
        solara.Markdown(f"* {series.total_videos} total videos")

        solara.Markdown(f"* {series.start_date} to {series.end_date}")

        solara.Button("Edit Series", on_click=lambda: SeriesForm())
        solara.Button("Delete Series", on_click=lambda: series.delete_instance())


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )
    solara.Button("Add Series", on_click=add_series)
    with solara.ColumnsResponsive(12, large=4):

        series = Series.select()
        for ser in series:
            SeriesCard(ser)
