import solara
from solara.lab.toestand import Ref

from hmtc.components.playlist.list_item import PlaylistListItem


@solara.component
def PlaylistCards(playlists, on_update, on_delete):

    with solara.ColumnsResponsive(12, large=4):
        for index, item in enumerate(playlists.value):
            # logger.debug(f"Rendering item {index} {item}")
            # logger.debug(f"Fields type = {type(playlists.fields)} 🔵🔵🔵")
            PlaylistListItem(
                Ref(playlists.fields[index]),
                on_update=on_update,
                on_delete=on_delete,
            )
            # logger.debug("On to the next field 🏠🏠🏠")
