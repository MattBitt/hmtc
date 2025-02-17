import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.sectionalizer.main import VideoFrame
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFiles as VideoFilesModel
from hmtc.utils.general import paginate

refresh_counter = solara.reactive(1)


@solara.component
def SecondRow(
    video: Video,
):
    error = solara.use_reactive("")
    success = solara.use_reactive("")
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
                # with solara.Link(f"/api/videos/finetuner/{video.instance.id}"):
                #     solara.Button(
                #         f"Fine Tuner",
                #         icon_name=Icons.FINETUNER.value,
                #         classes=["button"],
                #     )


@solara.component
def MainRow(video: Video):
    if video.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return
    with solara.Card():
        with solara.Columns():
            with solara.Column():
                solara.Image(video.poster(), width="400px")

        with solara.Row(justify="center"):
            solara.Text(f"{video.instance.title}")


@solara.component
def PaginatedVideos():
    current_page = solara.use_reactive(1)
    # omegle = Album.get_by(title="Omegle Bars")
    guerrilla = Album.get_by(title="Guerrilla Bars")
    base_query = VideoModel.select(VideoModel).where(
        (VideoModel.unique_content == True)
        & VideoModel.id.in_(
            SectionModel.select(SectionModel.video_id)
            .where(SectionModel.fine_tuned == False)
            .distinct()
        )
    )

    # if omegle is not None:
    #    base_query = base_query.where(VideoModel.id.in_(omegle.discs_and_videos()))
    # if guerrilla is not None:
    #     base_query = base_query.where(VideoModel.id.in_(guerrilla.discs_and_videos()))

    page_query = base_query.order_by(VideoModel.duration.asc())

    if len(page_query) == 0:
        solara.Warning(f"No Videos Found meeting these criteria.")
        return

    _query, num_items, num_pages = paginate(
        query=page_query,
        page=current_page.value,
        per_page=1,
    )

    if current_page.value > num_pages:
        current_page.set(num_pages)

    video = Video(_query.first())
    with solara.Row(justify="center"):
        solara.Markdown(
            f"#### Vids to Fine Tune (Has unfinished Sections - sorted by duration) (2/16/25)"
        )
    with solara.Row(justify="center"):
        MainRow(video)
    with solara.Row(justify="center"):
        SecondRow(video)
    with solara.Row(justify="center"):
        PaginationControls(
            current_page=current_page, num_pages=num_pages, num_items=num_items
        )


@solara.component
def Page():

    with solara.Column(classes=["main-container"]):

        PaginatedVideos()
