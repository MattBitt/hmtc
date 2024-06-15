import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.playlist.popover import PlaylistPopover
from hmtc.components.series.popover import SeriesPopover
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.shared.sort_controls import SortControls
from hmtc.components.video.cards_list import VideoCards
from hmtc.components.video.new_text_box import VideoSearchBox
from hmtc.config import init_config
from hmtc.schemas.video import VideoItem
from hmtc.states.base import State as BaseState

config = init_config()


@solara.component
def ScoreCard(label, value):
    with solara.Card():
        solara.Markdown(f"#### {label}")
        solara.Markdown(f"# {value}")


@solara.component
def FilteredVideosStats(label="Video Stats....", items=[]):
    total = len(items)
    if total == 0:
        with solara.Card(title=label):
            solara.Error("No videos found", icon="mdi-alert-circle-outline")
    else:

        with solara.Card(title=label):

            unique = [v for v in items if v.contains_unique_content]
            nonunique = total - len(unique)
            no_duration = [v for v in items if v.duration is None]
            with_duration = total - len(no_duration)
            manually_edited = [v for v in items if v.manually_edited]
            downloaded = VideoItem.count_vids_with_media_files()
            with solara.Row():
                ScoreCard("Unique", len(unique))
                ScoreCard("Non-Unique", nonunique)
                ScoreCard("No Duration", len(no_duration))
                ScoreCard("Has Duration", with_duration)
                ScoreCard("Manually Edited", len(manually_edited))
                ScoreCard("Videos Downloaded", downloaded)
                ScoreCard("Total", total)


def compute_number_of_pages(total_items, per_page):
    np = total_items / per_page
    return int(np) + 1 if np > int(np) else int(np)


class State(BaseState):
    logger.debug("Initializing VideosState object page = (Videos)")

    # initialize reactive variables
    text_query = solara.reactive("")
    sort_column = solara.reactive("title")
    sort_order = solara.reactive("asc")
    current_page = solara.reactive(1)
    per_page = solara.reactive(config["general"]["items_per_page"])
    playlist_filter = solara.reactive(None)
    series_filter = solara.reactive(None)
    include_no_durations = solara.reactive(True)
    include_unique_content = solara.reactive(True)
    include_nonunique_content = solara.reactive(False)
    include_manually_edited = solara.reactive(False)

    initial_items, filtered_items = VideoItem.grab_page_from_db(
        current_page=current_page.value,
        per_page=per_page.value,
        text_search=text_query.value,
        sort_column=sort_column.value,
        sort_order=sort_order.value,
        series_filter=series_filter.value,
        playlist_filter=playlist_filter.value,
        include_no_durations=include_no_durations.value,
        include_unique_content=include_unique_content.value,
        include_nonunique_content=include_nonunique_content.value,
        include_manually_edited=include_manually_edited.value,
    )
    if not initial_items:
        logger.error("DOes this always happen???? 🧬🧬🧬🧬🧬")
        num_pages = solara.reactive(1)
        items = solara.reactive([])
        filtered_items = solara.reactive([])
    else:
        # logger.debug(f"Initial items {initial_items}")
        items = solara.reactive(initial_items)

        # logger.debug(f"Filtered items {filtered_items}")
        filtered_items = solara.reactive(filtered_items)

        num_pages = solara.reactive(
            compute_number_of_pages(len(filtered_items.value), per_page.value)
        )

    @classmethod
    def stats(cls):
        stats = {
            "total": VideoItem.count_enabled(),
            "enabled": VideoItem.count_enabled(),
            "disabled": VideoItem.count_enabled(enabled=False),
            "no_duration": VideoItem.count_no_duration(),
            "unique": VideoItem.count_unique(),
        }

        return stats

    @classmethod
    def refresh_query(cls):
        logger.debug("refresh_query in Base State of Videos Page 🏠🏠🏠🏠🏠")

        cls.items.value, cls.filtered_items.value = VideoItem.grab_page_from_db(
            current_page=cls.current_page.value,
            per_page=cls.per_page.value,
            text_search=cls.text_query.value,
            sort_column=cls.sort_column.value,
            sort_order=cls.sort_order.value,
            series_filter=State.series_filter.value,
            playlist_filter=State.playlist_filter.value,
            include_no_durations=State.include_no_durations.value,
            include_unique_content=State.include_unique_content.value,
            include_nonunique_content=State.include_nonunique_content.value,
            include_manually_edited=State.include_manually_edited.value,
        )
        np = len(cls.filtered_items.value) / cls.per_page.value
        cls.num_pages.value = int(np) + 1 if np > int(np) else int(np)

    @classmethod
    def on_update_from_youtube(cls, item):
        logger.debug(f"on_update_from_youtube: {item}")
        item.update_from_youtube()
        cls.refresh_query()

    @classmethod
    def on_click_playlists(cls, *args):
        if args[0]:
            State.playlist_filter.value = args[0]
            State.refresh_query()

    @staticmethod
    def on_click_series(*args):
        if args[0]:
            if args[0].get("id") is None:
                State.series_filter.value = None
            else:
                logger.debug(args[0])
                State.series_filter.value = args[0]
            State.refresh_query()

    def clear_filters(*args):
        logger.debug("Clearing filters")
        State.series_filter.value = None
        State.playlist_filter.value = None
        State.refresh_query()


@solara.component
def Page():
    router = solara.use_router()
    refreshing = solara.use_reactive(False)

    def on_save(*args):
        logger.debug(f"on_save: {args}🤡🤡🤡🤡🤡")
        args[0].update_database_object()

    MySidebar(
        router=solara.use_router(),
    )
    with solara.Column(classes=["main-container", "mb-10"]):
        with solara.Row():

            SeriesPopover(
                current_series=State.series_filter.value,
                handle_click=State.on_click_series,
                include_blank=True,
            )
            PlaylistPopover(
                current_playlist=State.playlist_filter.value,
                handle_click=State.on_click_playlists,
            )

            solara.Button(
                "Clear Filters", classes=["button"], on_click=State.clear_filters
            )
            solara.Button(
                label="Refresh", on_click=State.refresh_query, classes=["button"]
            )

        with solara.Row():
            solara.Checkbox(label="Unique", value=Ref(State.include_unique_content))
            solara.Checkbox(
                label="Non-Unique", value=Ref(State.include_nonunique_content)
            )
            solara.Checkbox(
                label="Include No Durations", value=Ref(State.include_no_durations)
            )
        # searchable text box
        VideoSearchBox(on_change=State.on_change_text_search, on_new=State.on_new)
        # Results of the Filter
        FilteredVideosStats(label="Filtered Videos", items=State.filtered_items.value)

        # Sort the Videos
        SortControls(State)

        if refreshing.value:
            solara.SpinnerSolara()
        else:
            if State.items.value:
                PaginationControls(
                    current_page=State.current_page,
                    num_pages=State.num_pages,
                    on_page_change=State.on_page_change,
                )
                VideoCards(
                    Ref(State.items),
                    router=router,
                    refreshing=refreshing,
                    on_save=on_save,
                    on_delete=State.on_delete,
                    refresh_query=State.refresh_query,
                )
            else:
                if State.text_query.value != "":
                    solara.Error(
                        f"No videos found for {State.text_query.value}",
                        icon="mdi-alert-circle-outline",
                    )
                else:

                    solara.Error(
                        "No videos found and No text was entered",
                        icon="mdi-alert-circle-outline",
                    )
