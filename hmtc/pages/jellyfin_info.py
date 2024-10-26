import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.utils.jellyfin_functions import (
    get_user_favorites,
    can_ping_server,
    get_user_session,
)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown("## Jellyfin Info")
    solara.Markdown(str(can_ping_server()))
    solara.Markdown(f"{get_user_session()}")
