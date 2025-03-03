import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import PaginationControls
from hmtc.domains.album import Album
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import SectionTopic as SectionTopicModel
from hmtc.models import Video as VideoModel
from hmtc.models import VideoFiles as VideoFilesModel
from hmtc.utils.general import paginate

refresh_counter = solara.reactive(1)


@solara.component
def SecondRow(video: Video):
    error = solara.use_reactive("")
    success = solara.use_reactive("")

    with solara.Column():
        with solara.Card("Section That Needs Info"):
            with solara.Link(f"/api/videos/finetuner/{video.instance.id}"):
                solara.Button(
                    label=f"Fine Tuner",
                    icon_name=Icons.FINETUNER.value,
                    classes=["button"],
                )


@solara.component
def MainRow(video: Video):
    if video.instance is None:
        with solara.Row(justify="center"):
            solara.Error("Instance is None...")
            return
    with solara.Card():
        with solara.Row(justify="center"):
            solara.Text(f"{video.instance.title}")


@solara.component
def PaginatedVideos():
    current_page = solara.use_reactive(1)
    sections_with_topics = SectionTopicModel.select(
        SectionTopicModel.section_id
    ).distinct()
    sids = [s.section.id for s in sections_with_topics]
    sections = SectionModel.select().where(
        (SectionModel.fine_tuned == True)
        & ((SectionModel.title.is_null(True)) | (SectionModel.title == ""))
        & (SectionModel.id.not_in(sids))
    )
    # sections = all sections without a title or topics and marked fine_tuned
    # i want the video of each of these sections
    logger.debug(f"section ids found: {sids} ")
    vids_of_interest = [s.video_id for s in sections]
    logger.debug(f"Found {len(vids_of_interest)} videos with problematic sections")
    logger.debug(f"{vids_of_interest=}")
    base_query = VideoModel.select().where(VideoModel.id.in_(vids_of_interest))

    page_query = base_query.order_by(VideoModel.duration.asc())

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

    video = Video(_query.first())

    with solara.Row(justify="center"):
        solara.Markdown(f"#### Sections Fine Tuned - with no Info (2/27/25)")
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
