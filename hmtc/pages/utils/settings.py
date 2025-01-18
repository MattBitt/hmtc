from pathlib import Path

import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains.video import Video
from hmtc.models import ImageFile, OmegleSection, Thumbnail, VideoFiles
from hmtc.models import Video as VideoModel
from hmtc.repos.file_repo import create_thumbnail
from hmtc.utils.importer.existing_files import (
    create_omegle_sections,
    import_existing_video_files_to_db,
    import_sections,
)
from hmtc.utils.youtube_functions import download_video_file

config = init_config()
STORAGE = Path(config["STORAGE"])


def create_missing_thumbnails():
    images = ImageFile.select().where(ImageFile.id.not_in(Thumbnail.select()))
    for image in images:
        create_thumbnail(Path(image.path), image.id)


def download_unique():
    vids_missing_video = VideoFiles.select().where(VideoFiles.video_id.is_null())
    vids_missing_list = set([x.item_id for x in vids_missing_video])

    unique_vids = VideoModel.select(VideoModel.id).where(
        VideoModel.unique_content == True
    )
    unique_list = set([x.id for x in unique_vids])
    to_process = unique_list.intersection(vids_missing_list)
    downloaded = 0
    logger.debug(
        f"Found {len(to_process)} unique videos missing a video file. Downloading"
    )
    for vid_id in to_process:
        video = Video(vid_id)
        download_video_file(video.instance.youtube_id)
        downloaded += 1
        if downloaded >= 10:
            break


@solara.component
def SectionsControls():
    num_sections = OmegleSection.select().count()
    vids_missing_video = 15
    with solara.Columns():
        with solara.Card("Videos"):
            with solara.Column():
                solara.Text(f"Import Videos")
                solara.Button(
                    "Scan Local",
                    on_click=lambda: import_existing_video_files_to_db(
                        STORAGE / "videos"
                    ),
                    classes=["button"],
                )
                solara.Text(f"Create missing thumbnails")
                solara.Button(
                    f"Create missing Thumbnails",
                    on_click=create_missing_thumbnails,
                    classes=["button"],
                )
                solara.Button(
                    f"Download Unique Videos {vids_missing_video}",
                    on_click=download_unique,
                    classes=["button"],
                )
        with solara.Card("Sections"):
            with solara.Column():
                solara.Text(f"Import Sections")
                solara.Button(
                    "Seed Table from CSV", on_click=import_sections, classes=["button"]
                )
                solara.Button(
                    "Create Sections for Videos",
                    on_click=create_omegle_sections,
                    classes=["button"],
                )


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown(f"# Settings Page")
    SectionsControls()
