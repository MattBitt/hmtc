import solara

from hmtc.components.shared.dropdown import Dropdown
from hmtc.models import Playlist


@solara.component
def PlaylistDropdown(handle_click, color, current_playlist=None):
    playlists = Playlist.select().where(Playlist.title.is_null(False))
    items = [{"title": playlist.title, "id": playlist.id} for playlist in playlists]
    if current_playlist:
        caption = current_playlist["title"]
    else:
        caption = "All Playlists"
    Dropdown(
        items=items,
        caption=caption,
        handle_click=handle_click,
        color=color,
    )
