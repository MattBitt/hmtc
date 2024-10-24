from pathlib import Path
from typing import Dict
import PIL
import solara
import solara.lab
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Channel as ChannelModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem


config = init_config()

title = " "
busy_downloading = solara.reactive(False)


def refresh_from_youtube():
    busy_downloading.set(True)
    existing_ids = [v.youtube_id for v in VideoItem.get_youtube_ids()]
    channels = ChannelModel.select().where((ChannelModel.name.contains("Harry")))

    num_new_vids = 0

    for c in channels:
        yt_ids = c.grab_ids()
        ids_to_update = [id for id in yt_ids if id not in existing_ids]
        num_new_vids += len(ids_to_update)
        for id in ids_to_update:
            VideoItem.create_from_youtube_id(id)

    if num_new_vids == 0:
        logger.debug("No new videos found")
    else:
        logger.debug(f"Found {num_new_vids} new videos")
    busy_downloading.set(False)


@solara.component_vue("../components/shared/progress_circle.vue", vuetify=True)
def ProgressCircle():
    pass


@solara.component
def Page():
    image = PIL.Image.open(Path("hmtc/assets/images/harry-mack-logo.png"))

    MySidebar(
        router=solara.use_router(),
    )

    latest_vids = (
        VideoModel.select()
        .where(VideoModel.contains_unique_content == True)
        .order_by(VideoModel.upload_date.desc())
        .limit(3)
    )

    with solara.Column(
        classes=["main-container"], style={"background-color": Colors.BACKGROUND}
    ):
        with solara.Row(justify="center", style={"background-color": Colors.SURFACE}):
            if busy_downloading.value:
                ProgressCircle()
            else:

                solara.Button("Videos", classes=["button"], href="/videos")
                solara.Button("Tracks", classes=["button"], href="/tracks")

                solara.Button(
                    "Refresh", classes=["button"], on_click=refresh_from_youtube
                )
        with solara.Row():
            with solara.Column(
                align="center", style={"background-color": Colors.SURFACE}
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
