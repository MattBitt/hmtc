import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.playlist.list_item import PlaylistListItem
from hmtc.components.playlist.new_button import PlaylistNewButton
from hmtc.components.playlist.new_text_box import PlaylistNewTextBox
from hmtc.components.playlist.stats_display import StatsDisplay
from hmtc.config import init_config
from hmtc.schemas.playlist import PlaylistItem


class State:
    logger.debug("Initializing State object page = (Playlists)")
    config = init_config()

    text_query = solara.reactive("")
    sort_column = solara.reactive("title")
    sort_order = solara.reactive("asc")

    current_page = solara.reactive(1)
    per_page = solara.reactive(config["general"]["items_per_page"])

    initial_items, total_items = PlaylistItem.grab_page_from_db(
        current_page=current_page.value,
        per_page=per_page.value,
        text_search=text_query.value,
    )

    playlists = solara.reactive(initial_items)

    np = total_items / per_page.value
    num_pages = solara.reactive(int(np) + 1 if np > int(np) else int(np))

    @staticmethod
    def playlist_stats():
        stats = {
            "total": PlaylistItem.count_enabled(),
            "enabled": PlaylistItem.count_enabled(),
            "disabled": PlaylistItem.count_enabled(enabled=False),
            "unique": PlaylistItem.count_unique(),
            "non_unique": PlaylistItem.count_unique(unique=False),
        }

        return stats

    @staticmethod
    def on_new(item: PlaylistItem):
        logger.debug(f"on_new: {item}, {item.__class__}")
        logger.info(f"Adding new item: {item}")
        item.save_to_db()
        State.refresh_query()

    @staticmethod
    def on_delete(item: PlaylistItem):
        logger.debug(f"on_delete: {item}, {item.__class__}")
        logger.info(f"Deleting item: {item}")
        db_item = item.grab_id_from_db(id=item.id)
        db_item.my_delete_instance()
        State.refresh_query()

    @staticmethod
    def on_update(item: PlaylistItem):
        logger.debug(f"on_update: {item}, {item.__class__}")
        logger.info(f"Updating existing item: {item}")
        item.save_to_db()
        State.refresh_query()

    @staticmethod
    def on_change_text_search(text: str):
        logger.debug(f"on_change_text_search: {text}")
        State.text_query.value = text
        State.refresh_query()

    @staticmethod
    def on_page_change(page: int):
        logger.debug(f"on_page_change: {page}")
        State.current_page.value = page
        State.refresh_query()

    @staticmethod
    def refresh_query():
        logger.debug(f"refresh_query")
        State.playlists.value, total_items = PlaylistItem.grab_page_from_db(
            current_page=State.current_page.value,
            per_page=State.per_page.value,
            text_search=State.text_query.value,
            sort_column=State.sort_column.value,
            sort_order=State.sort_order.value,
        )
        np = total_items / State.per_page.value
        State.num_pages.value = int(np) + 1 if np > int(np) else int(np)


@solara.component
def PlaylistCards(playlists):

    with solara.ColumnsResponsive(12, large=4):
        for index, item in enumerate(playlists.value):
            # logger.debug(f"Rendering item {index} {item}")
            logger.debug(f"Fields type = {type(playlists.fields)} 🔵🔵🔵")
            PlaylistListItem(
                Ref(playlists.fields[index]),
                on_update=State.on_update,
                on_delete=State.on_delete,
            )
            logger.debug("On to the next field 🏠🏠🏠")


@solara.component
def Page():
    # example playlist url https://www.youtube.com/playlist?list=PLtbrIhAJmrPBf2DKh3UByQ6Q1D_rCSAiI

    def sort_by_date():
        State.sort_column.value = "created_at"
        State.sort_order.value = "asc"
        State.refresh_query()

    def sort_by_title():
        State.sort_column.value = "title"
        State.sort_order.value = "asc"
        State.refresh_query()

    with solara.Row():
        solara.Button(label="Sort by Title", on_click=sort_by_title)
        solara.Button(label="Sort by Date", on_click=sort_by_date)

    with solara.Card("Playlist list"):
        solara.Info("In Page and rendering Playlist list")

        PlaylistNewTextBox(on_change=State.on_change_text_search, on_new=State.on_new)
        if State.playlists.value:
            StatsDisplay(State.playlist_stats())
            PlaylistCards(Ref(State.playlists))
        else:
            if State.text_query.value != "":

                solara.Error(
                    f"No playlists found for {State.text_query.value}",
                    icon="mdi-alert-circle-outline",
                )
            else:
                solara.Error("No playlists found", icon="mdi-alert-circle-outline")

        # PlaylistNewButton(on_new=State.on_new)
        logger.debug(f"Number of pages = {State.num_pages}")
        if State.num_pages.value > 1:
            PaginationControls(
                current_page=State.current_page,
                num_pages=State.num_pages,
                on_page_change=State.on_page_change,
            )
