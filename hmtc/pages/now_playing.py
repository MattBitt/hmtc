import solara
from hmtc.schemas.video import VideoItem
from hmtc.utils.jf import grab_now_playing, pause_client, play_client, add_tag_to_item
from hmtc.components.shared.sidebar import MySidebar
from pathlib import Path


def get_youtube_id(filename):
    fn = Path(filename).stem
    if "___" not in fn:
        return None
    return fn.split("___")[1]


@solara.component
def RatingStars():
    with solara.Row():
        for i in range(1, 6):
            solara.Button("⭐️" * i, on_click=lambda: add_tag_to_item(f"star:{i}"))


@solara.component
def Page():

    new_tag = solara.reactive("")

    def pause(*ignore_args):
        pause_client()

    def seek_forward(ms, *ignore_args):
        pass

    def add_tag(*ignore_args):
        add_tag_to_item(new_tag.value)

    MySidebar(
        router=solara.use_router(),
    )

    with solara.Column(classes=["main-container"]):
        solara.Markdown("Now Playing Page!")
        now_playing = grab_now_playing()
        if now_playing:
            if now_playing["type"] == "track":
                solara.Markdown("### This is a track playing, somehow....")
            else:
                solara.Markdown(f"### {now_playing}")
                youtube_id = get_youtube_id(now_playing["path"])
                vid = VideoItem.get_by_youtube_id(youtube_id)
                if vid:
                    solara.Markdown(f"#### Video Title: {vid.title}")
                    solara.Markdown(f"#### Video ID: {youtube_id}")
                    solara.Markdown(f"#### Jellyfin ID: {now_playing['jf_id']}")
                    # solara.Markdown(f"#### Rating: {now_playing['rating']}")
                    solara.Markdown(f"#### Currently Playing: {now_playing['type']}")
                    solara.Button("Play", on_click=play_client)
                    solara.Button("Pause", on_click=pause)
                    solara.Button(
                        "Seek Forward 10s", on_click=lambda: seek_forward(10_000_000)
                    )
                    RatingStars()
                    with solara.Card():
                        solara.InputText("Tag", continuous_update=False, value=new_tag)
                        solara.Button("Add Tag", on_click=add_tag)

                else:
                    solara.Markdown("### Video not found in database")
        else:
            solara.Markdown("### No video currently playing")
