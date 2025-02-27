import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFiles as VideoFilesModel
from hmtc.utils.general import paginate

refresh_counter = solara.reactive(1)


@solara.component
def SecondRow(
    section: Section
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")
    video = Video()
    unique = solara.use_reactive(video.instance.unique_content)

    def toggle_unique():
        new_unique = not video.instance.unique_content
        video.instance.unique_content = new_unique
        video.instance.save()
        unique.set(new_unique)
        refresh_counter.set(refresh_counter.value + 1)

    with solara.Column():

        with solara.Card("Other"):

            with solara.ColumnsResponsive():
                solara.Button(
                    f"Unique: {str(unique.value)}",
                    on_click=toggle_unique,
                    icon_name=Icons.UNIQUE.value,
                    classes=["button"],
                )
                with solara.Link(f"/api/videos/sectionalizer/{video.instance.id}"):
                    solara.Button(
                        f"Sectionalizer",
                        icon_name=Icons.SECTION.value,
                        classes=["button"],
                    )
                with solara.Link(f"/api/videos/finetuner/{video.instance.id}"):
                    solara.Button(
                        f"Fine Tuner",
                        icon_name=Icons.FINETUNER.value,
                        classes=["button"],
                    )


@solara.component
def MainRow(section: Section):
    if section.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return
    with solara.Card():
        with solara.Row(justify="center"):
            solara.Text(f"{section.instance.title}")


@solara.component
def PaginatedVideos():
    current_page = solara.use_reactive(1)

    base_query = (
        SectionModel.select().where((SectionModel.fine_tuned == True) & (SectionModel.title.is_null(True)))
    )


    page_query = base_query.order_by(SectionModel.id.asc())

    if len(page_query) == 0:
        solara.Warning(f"No Sections Found meeting these criteria.")
        return

    _query, num_items, num_pages = paginate(
        query=page_query,
        page=current_page.value,
        per_page=1,
    )

    if current_page.value > num_pages:
        current_page.set(num_pages)

    section = Section(_query.first())
    with solara.Row(justify="center"):
        solara.Markdown(
            f"#### Sections Fine Tuned - with no Info (2/27/25)"
        )
    with solara.Row(justify="center"):
        MainRow(section)
    with solara.Row(justify="center"):
        SecondRow(section)
    with solara.Row(justify="center"):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )


@solara.component
def Page():

    with solara.Column(classes=["main-container"]):

        PaginatedVideos()
