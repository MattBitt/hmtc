import solara
from dataclasses import dataclass
from hmtc.models import Series, Video, Section
from datetime import date, datetime

all_languages = "Python C++ Java JavaScript TypeScript BASIC".split()
languages = solara.reactive([all_languages[0]])

all_series = [s.name for s in Series.select()]
selected_series = solara.reactive(all_series)

title_query = solara.reactive("")
per_page = solara.reactive(10)
sort_by = solara.reactive("upload_date")
sort_order = solara.reactive("desc")

num_pages = solara.reactive(0)
current_page = solara.reactive(1)


@solara.component
def VideoCard(video):
    with solara.Card(video.title):
        with solara.Row():
            solara.Markdown(f"**Sections**: {video.sections.count()}")
            solara.Markdown(f"**Files**: {video.files.count()}")
            solara.Markdown(f"**Duration**: {video.duration}")
        with solara.CardActions():
            with solara.Link(f"/videos/{video.id}"):
                solara.Button("Edit")
            solara.Button("Delete")


@solara.component
def MultiSelect(title, selected, all):
    with solara.Div():
        # solara.ToggleButtonsMultiple(selected, all, dense=True, style={"color": "blue"})

        def on_click(item):
            if item not in selected.value:
                selected.value.append(item)
            else:
                selected.value.remove(item)

        with solara.ToggleButtonsMultiple(value=selected, dense=True):
            # with solara.ColumnsResponsive(3):
            for item in all:
                solara.Button(
                    item,
                    value=item,
                    on_click=lambda: on_click(item),
                )


@solara.component
def SingleSelect(title, selected, all):
    with solara.Div():
        solara.ToggleButtonsSingle(selected, all)
        # solara.Markdown(f"**Selected**: {selected.value}")


@solara.component
def SortToolBar():
    with solara.Card("Sorting"):
        with solara.Row(justify="space-between"):
            SingleSelect("Sort By", sort_by, ["upload_date", "title"])
            SingleSelect("Sort Order", sort_order, ["asc", "desc"])


@solara.component
def Pagination():
    with solara.Card("Pagination"):

        solara.Button(
            "First",
            on_click=lambda: current_page.set(1),
            disabled=(current_page.value == 1),
        )
        solara.Button(
            "Previous",
            on_click=lambda: current_page.set(current_page.value - 1),
            disabled=(current_page.value == 1),
        ),

        solara.Button(
            "Next",
            on_click=lambda: current_page.set(current_page.value + 1),
            disabled=(current_page.value == num_pages.value),
        )
        solara.Button(
            "Last",
            on_click=lambda: current_page.set(num_pages.value),
            disabled=(current_page.value == num_pages.value),
        )
        SingleSelect("Videos per page", per_page, [5, 10, 20, 50, 100])
        solara.Markdown(f"Page {current_page.value} of {num_pages.value}")


@solara.component
def SeriesFilterCard():
    with solara.Card(title="Series"):
        MultiSelect("Series", selected_series, all_series)
        with solara.CardActions():
            solara.Button("Clear", on_click=lambda: selected_series.set([]))
            solara.Button(
                "Select All", on_click=lambda: selected_series.set(all_series)
            )


@solara.component
def TitleTextFilter():
    with solara.Card():
        solara.InputText(
            "Search Video Titles", value=title_query, continuous_update=True
        )


@solara.component
def Page():

    # this sql will return all videos that have more than 1 section
    # SELECT video.*, (SELECT COUNT(*) FROM section WHERE section.video_id = video.id) AS TOT FROM video where TOT > 1;
    SeriesFilterCard()
    with solara.ColumnsResponsive(12, large=4):

        TitleTextFilter()
        SortToolBar()

    query = Video.select().join(Series).where(Series.name.in_(selected_series.value))

    if title_query.value:
        query = query.where(Video.title.contains(title_query.value))
    solara.Markdown(f"## Total: {query.count()} videos found.")

    sort_mapping = {
        ("upload_date", "asc"): Video.upload_date.asc(),
        ("upload_date", "desc"): Video.upload_date.desc(),
        ("title", "asc"): Video.title.asc(),
        ("title", "desc"): Video.title.desc(),
    }
    query = query.order_by(sort_mapping.get((sort_by.value, sort_order.value)))

    num_pages.set(query.count() // per_page.value + 1)
    if current_page.value > num_pages.value:
        current_page.set(1)
    with solara.ColumnsResponsive(12, large=4):
        for video in query.paginate(current_page.value, per_page.value):
            VideoCard(video)

    Pagination()
