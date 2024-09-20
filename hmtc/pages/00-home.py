import solara
import solara.lab
from pathlib import Path
import PIL
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.assets.colors import Colors

config = init_config()


@solara.component
def Page():
    image = PIL.Image.open(Path("hmtc/assets/images/harry-mack-logo.png"))
    image2 = PIL.Image.open(Path("hmtc/assets/images/harry-mack-logo-inverted.png"))
    MySidebar(
        router=solara.use_router(),
    )
    latest_vids = (
        VideoModel.select()
        .where(VideoModel.contains_unique_content == True)
        .order_by(VideoModel.id.desc())
        .limit(6)
    )

    with solara.Column(classes=["main-container"]):
        with solara.Columns([1, 4, 1]):
            solara.Markdown("")
            with solara.Row(
                justify="center", style={"background-color": Colors.SURFACE}
            ):
                solara.Button("Videos", classes=["button"], href="/video-table")
                solara.Button("Serieses", classes=["button"], href="/series")
                solara.Button("Albums", classes=["button"], href="/albums")
                solara.Button("Tracks", classes=["button"], href="/tracks")
            solara.Markdown("")
        with solara.Row(style={"height": "30%"}):
            with solara.Column(
                align="center",
                style={
                    "background-color": Colors.SURFACE,
                    # "position": "absolute",
                    # "top": "0",
                    # "left": "0",
                    "width": "100%",
                    "height": "20%",
                },
            ):
                solara.Image(image=image)

        with solara.ColumnsResponsive(default=12, large=4):
            for vid in latest_vids:
                poster = FileManager.get_file_for_video(vid, "poster")
                vid_image = PIL.Image.open(Path(str(poster)))

                with solara.Card():
                    with solara.Column():
                        with solara.Link(f"/video-details/{vid.id}"):
                            solara.Image(image=vid_image)
                        solara.Markdown(f"#### {vid.title}")
