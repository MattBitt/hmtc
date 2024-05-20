import solara
from loguru import logger

from hmtc.config import init_config
from hmtc.schemas.playlist import PlaylistItem
from hmtc.states.base import State


def compute_number_of_pages(total_items, per_page):
    np = total_items / per_page
    return int(np) + 1 if np > int(np) else int(np)


class PlaylistsState(State):
    logger.debug("Initializing PlaylistsState object page = (Playlists)")
    config = init_config()

    # initialize reactive variables
    text_query = solara.reactive("")
    sort_column = solara.reactive("title")
    sort_order = solara.reactive("asc")
    current_page = solara.reactive(1)
    per_page = solara.reactive(config["general"]["items_per_page"])

    initial_items, total_items = PlaylistItem.grab_page_from_db(
        current_page=current_page.value,
        per_page=per_page.value,
        text_search=text_query.value,
        sort_column=sort_column.value,
        sort_order=sort_order.value,
    )

    playlists = solara.reactive(initial_items)
    num_pages = solara.reactive(compute_number_of_pages(total_items, per_page.value))

    @classmethod
    def playlist_stats(cls):
        stats = {
            "total": PlaylistItem.count_enabled(),
            "enabled": PlaylistItem.count_enabled(),
            "disabled": PlaylistItem.count_enabled(enabled=False),
            "unique": PlaylistItem.count_unique(),
            "non_unique": PlaylistItem.count_unique(unique=False),
        }

        return stats

    @classmethod
    def refresh_query(cls):
        logger.debug("refresh_query")
        cls.playlists.value, total_items = PlaylistItem.grab_page_from_db(
            current_page=cls.current_page.value,
            per_page=cls.per_page.value,
            text_search=cls.text_query.value,
            sort_column=cls.sort_column.value,
            sort_order=cls.sort_order.value,
        )
        np = total_items / cls.per_page.value
        cls.num_pages.value = int(np) + 1 if np > int(np) else int(np)
