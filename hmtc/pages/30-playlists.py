import solara
from loguru import logger
from solara.lab.toestand import Ref

from hmtc.components.pagination_controls import PaginationControls
from hmtc.components.playlist.playlist_list_item import PlaylistListItem
from hmtc.components.playlist.playlist_new_button import PlaylistNewButton
from hmtc.components.playlist.playlist_new_text_box import PlaylistNewTextBox
from hmtc.components.playlist.stats_display import StatsDisplay
from hmtc.config import init_config
from hmtc.schemas.playlist import PlaylistItem


class State:
    logger.debug("Initializing State object page = (Playlists)")
    config = init_config()
    title_query = solara.reactive("")

    current_page = solara.reactive(1)
    per_page = solara.reactive(config["general"]["items_per_page"])

    initial_items = PlaylistItem.grab_page_from_db(
        current_page=current_page.value, per_page=per_page.value
    )
    playlists = solara.reactive(initial_items)
    np = PlaylistItem.count_enabled() / per_page.value
    num_pages = solara.reactive(int(np) + 1 if np > int(np) else int(np))

    @staticmethod
    def total_playlist_count():
        return PlaylistItem.count_enabled()

    @staticmethod
    def on_new(item: PlaylistItem):
        logger.debug(f"on_new: {item}, {item.__class__}")
        logger.info(f"Adding new item: {item}")
        item.save_to_db()
        State.playlists.value = PlaylistItem.grab_page_from_db(
            current_page=State.current_page.value, per_page=State.per_page.value
        )

    @staticmethod
    def on_delete(item: PlaylistItem):
        logger.debug(f"on_delete: {item}, {item.__class__}")
        logger.info(f"Deleting item: {item}")
        db_item = item.grab_id_from_db(id=item.id)
        db_item.my_delete_instance()
        State.playlists.value = PlaylistItem.grab_page_from_db(
            current_page=State.current_page.value, per_page=State.per_page.value
        )

    @staticmethod
    def on_update(item: PlaylistItem):
        logger.debug(f"on_update: {item}, {item.__class__}")
        logger.info(f"Updating existing item: {item}")
        item.save_to_db()
        State.playlists.value = PlaylistItem.grab_page_from_db(
            current_page=State.current_page.value, per_page=State.per_page.value
        )

    @staticmethod
    def on_page_change(page: int):
        logger.debug(f"on_page_change: {page}")
        State.current_page.value = page
        State.playlists.value = PlaylistItem.grab_page_from_db(
            current_page=State.current_page.value, per_page=State.per_page.value
        )


@solara.component
def Page():
    with solara.Card("Playlist list"):
        PlaylistNewTextBox(on_new=State.on_new)
        if State.playlists.value:
            StatsDisplay(State.playlists, State.total_playlist_count())
            with solara.ColumnsResponsive(4):
                for index, item in enumerate(State.playlists.value):
                    PlaylistListItem(
                        Ref(State.playlists.fields[index]),
                        on_update=State.on_update,
                        on_delete=State.on_delete,
                    )
        else:
            solara.Info("No playlist items, enter some text above, and hit enter")
        PlaylistNewButton(on_new=State.on_new)
        PaginationControls(
            current_page=State.current_page,
            num_pages=State.num_pages,
            on_page_change=State.on_page_change,
        )
