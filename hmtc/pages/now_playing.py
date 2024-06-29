import solara
from hmtc.schemas.video import VideoItem
from hmtc.utils.jf import grab_now_playing, pause_client, play_client
from hmtc.components.shared.sidebar import MySidebar
from pathlib import Path


def get_youtube_id(filename):
    fn = Path(filename).stem
    if "___" not in fn:
        return None
    return fn.split("___")[1]


@solara.component
def Page():
    def pause():
        pause_client()

    router = solara.use_router()
    MySidebar(
        router=router,
    )
    with solara.Column(classes=["main-container"]):
        solara.Markdown("Now Playing Page!")
        now_playing = grab_now_playing()
        if now_playing:
            solara.Markdown(f"### {now_playing}")
            youtube_id = get_youtube_id(now_playing["path"])
            vid = VideoItem.get_by_youtube_id(youtube_id)
            if vid:
                solara.Markdown(f"#### Video Title: {vid.title}")
                solara.Markdown(f"#### Video ID: {youtube_id}")
                solara.Button("Play", on_click=play_client)
                solara.Button("Pause", on_click=pause)
                solara.Button(
                    "Seek Forward 10s", on_click=lambda: seek_forward(10_000_000)
                )
            else:
                solara.Markdown("### Video not found in database")
        else:
            solara.Markdown("### No video currently playing")
