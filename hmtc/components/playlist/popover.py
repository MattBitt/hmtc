import solara

from hmtc.models import Playlist


@solara.component_vue("../shared/popover.vue")
def _Popover(items, caption, event_on_click):
    pass


@solara.component
def PlaylistPopover(current_playlist, handle_click):
    playlists = (
        Playlist.select().where(Playlist.title.is_null(False)).order_by(Playlist.title)
    )
    items = [{"title": playlist.title, "id": playlist.id} for playlist in playlists]
    if current_playlist:
        caption = current_playlist["title"]
    else:
        caption = "All Playlists"
    _Popover(
        items=items,
        caption=caption,
        event_on_click=handle_click,
    )
