import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls

from hmtc.components.series.popover import SeriesPopover
from hmtc.components.youtube_series.popover import YoutubeSeriesPopover
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.video.cards_list import VideoCards
from hmtc.config import init_config
from hmtc.schemas.video import VideoItem
from hmtc.states.base import State as BaseState

config = init_config()

page_filtered = solara.reactive(False)
filter_status = solara.reactive("None")


def on_save_in_edit(*args):
    if args[0] is None:
        logger.error("No video item to save")
        return

    logger.debug(f"Saving: {args[0].title}")
    args[0].update_database_object()


def compute_number_of_pages(total_items, per_page):
    np = total_items / per_page
    return int(np) + 1 if np > int(np) else int(np)


@solara.component()
def SortButton(label, col_name, sort_by, sort_order, on_click):
    if sort_by == col_name:
        if sort_order == "asc":
            icon_name = "mdi-arrow-up-bold"
        else:
            icon_name = "mdi-arrow-down-bold"
    else:
        icon_name = ""

    solara.Button(label=label, icon_name=icon_name, on_click=on_click)


@solara.component
def PageHeader():

    def sort_by_title():
        State.sort_by.set("title")
        if State.sort_order.value == "asc":
            State.sort_order.set("desc")
        else:
            State.sort_order.set("asc")

        State.apply_filters()

    with solara.Row():
        if not page_filtered.value:

            SeriesPopover(
                current_series=State.series_filter.value,
                handle_click=State.on_click_series,
            )

            YoutubeSeriesPopover(
                current_youtube_series=State.youtube_series_filter.value,
                handle_click=State.on_click_youtube_series,
            )
        else:
            if State.series_filter.value:
                SeriesPopover(
                    current_series=State.series_filter.value,
                    handle_click=State.on_click_series,
                )
            elif State.youtube_series_filter.value:
                YoutubeSeriesPopover(
                    current_youtube_series=State.youtube_series_filter.value,
                    handle_click=State.on_click_youtube_series,
                )
            solara.Button(
                "Clear Filters", classes=["button"], on_click=State.clear_filters
            )
            with solara.Row():
                solara.Markdown(f"## Current Filters: {filter_status.value}")
    with solara.Row():
        # solara.Button("Title Ascending", on_click=sort_title_ascending)
        SortControls(State)
        solara.Checkbox(label="Include Nonunique", value=State.include_nonunique)
        solara.Button(
            label="Apply Filters", on_click=State.apply_filters, classes=["button"]
        )
        solara.Markdown(
            f"## Current Sort: {State.sort_by.value} {State.sort_order.value}"
        )


class State(BaseState):
    logger.debug("Initializing State object on Videos New Page")
    per_page = solara.reactive(config["general"]["items_per_page"])

    current_page = solara.reactive(1)

    series_filter = solara.reactive(None)
    youtube_series_filter = solara.reactive(None)

    sort_by = solara.reactive("upload_date")
    sort_order = solara.reactive("asc")

    include_nonunique = solara.reactive(False)

    video_ids = VideoItem.get_base_video_ids()

    logger.debug(f"Found {len(video_ids)} videos")

    if not video_ids:
        logger.error("No Videos Found")
        num_pages = solara.reactive(1)
        page_items = solara.reactive([])

    else:

        num_pages = solara.reactive(
            compute_number_of_pages(len(video_ids), per_page.value)
        )
        ids = video_ids[(current_page.value - 1) * per_page.value : per_page.value]
        vis = VideoItem.grab_list_of_video_details(ids=ids)

        page_items = solara.reactive(vis)

    @staticmethod
    def apply_filters():
        logger.debug("Applying filters")

        if State.series_filter.value:
            page_filtered.set(True)
            filter_status.set(f"Series: {State.series_filter.value['title']}")
        elif State.youtube_series_filter.value:
            page_filtered.set(True)
            filter_status.set(
                f"Youtube Series: {State.youtube_series_filter.value['title']}"
            )
        else:
            page_filtered.set(False)
            filter_status.set("None")

        State.video_ids = VideoItem.get_filtered_video_ids(
            series_filter=State.series_filter.value,
            youtube_series_filter=State.youtube_series_filter.value,
            sort_by=State.sort_by.value,
            sort_order=State.sort_order.value,
            include_nonunique_content=State.include_nonunique.value,
        )

        State.load_page_number(1)

        logger.debug(f"Found {len(State.video_ids)} videos")

        if not State.video_ids:
            logger.debug("🐹🐹🐹🐹 8-30-24 Does this ever happen? No Videos Found")
            solara.reactive(1)
            solara.reactive([])
        else:
            State.num_pages.set(
                compute_number_of_pages(len(State.video_ids), State.per_page.value)
            )
            ids = State.video_ids[
                (State.current_page.value - 1)
                * State.per_page.value : State.per_page.value
            ]
            if ids == ([], []):
                logger.debug("No videos found")

                return

            vis = VideoItem.grab_list_of_video_details(ids=ids)

            State.page_items.set(vis)

    @staticmethod
    def load_page_number(page_number):
        State.current_page.set(page_number)
        State.refresh_page_items()

    @staticmethod
    def refresh_page_items():

        logger.debug("Refreshing page contents - Videos-New")
        page = State.current_page.value
        per_page = State.per_page.value

        ids = State.video_ids[(page - 1) * per_page :][:per_page]
        if ids == ([], []):
            logger.debug("No videos found")

            return

        vis = VideoItem.grab_list_of_video_details(ids=ids)
        State.page_items.set(vis)

    @staticmethod
    def on_click_series(*args):
        if args[0]:
            if args[0].get("id") is None:
                State.series_filter.value = None
            else:
                logger.debug(args[0])
                State.series_filter.value = args[0]
            State.apply_filters()

    @staticmethod
    def on_click_youtube_series(*args):
        if args[0]:
            if args[0].get("id") is None:
                State.youtube_series_filter.value = None
            else:
                logger.debug(args[0])
                State.youtube_series_filter.value = args[0]
            State.apply_filters()

    @staticmethod
    def clear_filters():
        logger.debug("Clearing filters")
        State.series_filter.value = None
        State.youtube_series_filter.value = None
        State.apply_filters()


@solara.component
def Page():
    router = solara.use_router()
    refreshing = solara.use_reactive(False)
    # State.apply_filters()
    MySidebar(
        router=router,
    )

    def on_page_change_local(*args):
        logger.debug(f"on_page_change_local: {args}")
        new_page = args[0]
        State.load_page_number(new_page)

    with solara.Column(classes=["main-container", "mb-10"]):

        PageHeader()
        if refreshing.value:
            solara.SpinnerSolara()
        else:
            if State.page_items.value:

                PaginationControls(
                    current_page=State.current_page,
                    num_pages=State.num_pages,
                    on_page_change=on_page_change_local,
                )
                VideoCards(
                    Ref(State.page_items),
                    router=router,
                    refreshing=refreshing,
                    on_save=on_save_in_edit,
                    on_delete=State.on_delete,
                    refresh_query=State.refresh_page_items,
                )
            else:
                solara.Error(
                    "No videos found and No text was entered",
                    icon="mdi-alert-circle-outline",
                )
