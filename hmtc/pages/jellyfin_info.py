import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.my_jellyfin_client import MyJellyfinClient
from hmtc.store import store_in_session_storage, read_from_session_storage


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown("Hello, Jellyfin!")
    jf = MyJellyfinClient()
    jf.connect()

    solara.Text(f"Jellyfin object: {jf}")
    store_in_session_storage("jf_status", {"somestatus": "connected"})
