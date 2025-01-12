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
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.video import Video
from hmtc.utils.importer.existing_files import import_existing_video_files_to_db
from hmtc.utils.importer.seed_database import recreate_database
from hmtc.utils.opencv.image_manager import ImageManager

config = init_config()
STORAGE = Path(config["STORAGE"])
title = " "
busy_downloading = solara.reactive(False)


def refresh_from_youtube():
    busy_downloading.set(True)

    busy_downloading.set(False)


def scan_local_storage():

    import_existing_video_files_to_db(
        STORAGE / "videos", delete_premigration_superchats=True
    )


def ProgressCircle():
    solara.Markdown("## Refreshing from YouTube...")


@solara.component
def Page():

    MySidebar(
        router=solara.use_router(),
    )

    empty_db = Series.count() == 0
    vids_imported = Video.count() > 0
    latest_videos = Video.latest(3)

    with solara.Column(classes=["main-container"]):
        with solara.Row(justify="center", style={"background-color": Colors.SURFACE}):
            if busy_downloading.value:
                ProgressCircle()
            else:

                with solara.Link("/tables/videos/"):
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
                    disabled=True,
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
                        solara.Button(
                            f"Scan Local Storage...",
                            classes=["button"],
                            on_click=scan_local_storage,
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
                    # poster = FileManager.get_file_for_video(vid, "poster")

                    with solara.Card():
                        with solara.Column():
                            with solara.Link(f"/tables/video-details/{vid.id}"):
                                solara.Image(image=Video(vid).poster(), width="300px")
                            solara.Markdown(f"#### {vid.title}")
