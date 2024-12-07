from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import PIL
import solara
import solara.lab
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.utils.seed_database import seed_database
from hmtc.domains.channel import Channel
from hmtc.models import Video as VideoModel
from hmtc.pages.settings import PageState
from hmtc.schemas.file import FileManager
from hmtc.schemas.video import VideoItem
from hmtc.utils.opencv.image_manager import ImageManager

config = init_config()

title = " "
busy_downloading = solara.reactive(False)


def refresh_from_youtube():
    busy_downloading.set(True)
    existing_ids = [
        v.youtube_id
        for v in VideoModel.select(VideoModel.youtube_id).where(
            VideoModel.youtube_id.is_null(False)
        )
    ]
    channels = Channel().to_auto_update()

    num_new_vids = 0

    for c in channels:
        logger.debug(f"Checking channel {c.channel.title}")
        yt_ids = c.grab_ids()
        ids_to_update = [id for id in yt_ids if id not in existing_ids]
        num_new_vids += len(ids_to_update)
        c.last_update_completed = datetime.now()
        c.save()
        for id in ids_to_update[:5]:
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

    MySidebar(
        router=solara.use_router(),
    )

    channels = list(Channel().get_all())

    if len(channels) == 0:
        empty_db = True
        last_updated = None
        can_refresh = False
    else:
        empty_db = False
        last_updated = Channel().last_update_completed()

        if last_updated is None:
            can_refresh = True
        else:
            # how_long_ago_refreshed = datetime.now() - last_updated
            # can_refresh = how_long_ago_refreshed > timedelta(hours=1)
            can_refresh = True

        latest_vids = (
            VideoModel.select()
            .where(VideoModel.contains_unique_content == True)
            .order_by(VideoModel.upload_date.desc())
            .limit(3)
        )

    with solara.Column(classes=["main-container"]):
        with solara.Row(justify="center", style={"background-color": Colors.SURFACE}):
            if busy_downloading.value:
                ProgressCircle()
            else:

                solara.Button("Videos", classes=["button"], href="/videos")
                solara.Button("Tracks", classes=["button"], href="/tracks")

                solara.Button(
                    "Refresh",
                    classes=["button"],
                    on_click=refresh_from_youtube,
                    disabled=not can_refresh,
                )
        with solara.Column(align="center", style={"background-color": Colors.SURFACE}):
            logo_image = ImageManager(Path("hmtc/assets/images/harry-mack-logo.png"))
            solara.Image(image=logo_image.image)

        if empty_db:
            with solara.Row(justify="center"):
                with solara.Column():
                    solara.Text(
                        f"#### No channels found in the database. Hope this is a fresh install.",
                        classes=["primary--text"],
                    )
                    solara.Button(
                        f"Setup New Database...",
                        classes=["button"],
                        on_click=seed_database,
                    )
        else:
            with solara.ColumnsResponsive(default=12, large=4):
                for vid in latest_vids:
                    poster = FileManager.get_file_for_video(vid, "poster")
                    video_image = ImageManager(poster)

                    with solara.Card():
                        with solara.Column():
                            with solara.Link(f"/video-details/{vid.id}"):
                                solara.Image(image=video_image.image)
                            solara.Markdown(f"#### {vid.title}")
