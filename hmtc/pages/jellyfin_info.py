import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.utils.my_jellyfin_client import MyJellyfinClient


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown("Hello, Jellyfin!")
    jf = MyJellyfinClient()
    jf.connect()

    solara.Text(f"Jellyfin object: {jf}")
