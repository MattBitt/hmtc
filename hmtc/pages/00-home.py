from pathlib import Path
from typing import Dict

import solara
import solara.lab
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.video import Video
from hmtc.utils.importer.existing_files import (
    create_video_from_folder,
)
from hmtc.utils.importer.seed_database import recreate_database
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.youtube_functions import fetch_ids_from, get_video_info

config = init_config()
STORAGE = Path(config["STORAGE"])
WORKING = Path(config["WORKING"])

title = " "
busy_downloading = solara.reactive(False)


def refresh_from_youtube():
    busy_downloading.set(True)

    for channel in Channel.to_auto_update():
        logger.debug(f"Checking channel {channel}")
        not_in_db = []
        ids = fetch_ids_from(channel)
        for youtube_id in ids:
            vid = Video.get_by(youtube_id=youtube_id)
            if vid is None:
                not_in_db.append(youtube_id)

        logger.debug(f"Found {len(ids)} videos at {channel}")
        logger.debug(f"{len(not_in_db)} of them need to be added.")
        if config["general"]["environment"] == "development":
            items = not_in_db[:1]
        else:
            items = not_in_db
        for youtube_id in items:
            get_video_info(youtube_id, WORKING / youtube_id)

            create_video_from_folder(WORKING / youtube_id)

    busy_downloading.set(False)


def ProgressCircle():
    solara.Markdown("## Refreshing from YouTube...")


@solara.component
def Page():

    MySidebar(
        router=solara.use_router(),
    )

    empty_db = Series.count() == 0
    vids_imported = Video.count() > 0
    latest_videos = Video.latest(6)

    with solara.Column(classes=["main-container"]):
        with solara.Row(justify="center", style={"background-color": Colors.SURFACE}):
            if busy_downloading.value:
                ProgressCircle()
            else:

                with solara.Link("/tables/videos/unique"):
                    solara.Button("Videos", classes=["button"])
                with solara.Link("/tables/tracks/"):
                    solara.Button("Tracks", classes=["button"])
                with solara.Link("/dashboards/domains/"):
                    solara.Button(
                        "Domains", classes=["button"], href="/dashboards/domains"
                    )
                with solara.Link("/dashboards/files/"):
                    solara.Button(
                        "Files", classes=["button"], href="/dashboards/domains"
                    )
                solara.Button(
                    "Refresh",
                    classes=["button"],
                    on_click=refresh_from_youtube,
                    disabled=False,
                )

        with solara.Column(align="center", style={"background-color": Colors.SURFACE}):
            logo_image = ImageManager(Path("hmtc/assets/images/harry-mack-logo.png"))
            solara.Image(image=logo_image.image)

        if empty_db:
            with solara.Row(justify="center"):
                with solara.Column():
                    solara.Text(
                        f"#### No Series found in the database. Hope this is a fresh install.",
                        classes=["primary--text"],
                    )
                    solara.Button(
                        f"Setup New Database...",
                        classes=["button"],
                        on_click=recreate_database,
                    )
        if not vids_imported:
            with solara.Row(justify="center"):

                with solara.Columns([6, 6]):
                    with solara.Card():
                        solara.Text(
                            f"#### No Videos found in the database. Scan the local storage for videos.",
                            classes=["primary--text"],
                        )

                    with solara.Card():
                        solara.Text(
                            f"#### No Videos found in the database. Please refresh from YouTube.",
                            classes=["primary--text"],
                        )

                        solara.Button(
                            f"Refresh from YouTube...",
                            classes=["button"],
                            on_click=refresh_from_youtube,
                        )

        else:
            with solara.ColumnsResponsive(default=12, large=4):
                for vid in latest_videos:
                    with solara.Card():
                        with solara.Column():
                            with solara.Link(f"/domains/video-details/{vid.id}"):
                                solara.Image(
                                    image=Video(vid).poster(thumbnail=False),
                                    width="300px",
                                )
                            solara.Markdown(f"#### {vid.title}")
