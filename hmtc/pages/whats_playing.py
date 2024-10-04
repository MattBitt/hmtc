import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.my_jellyfin_client import MyJellyfinClient


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown(f"## What's Playing")
    jf = MyJellyfinClient()
    jf.connect()
    if jf.has_active_session():
        solara.Markdown(f"{jf.active_session}")
    else:
        solara.Markdown(f"No active session")
