from pathlib import Path

import peewee
import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import ImageFile, OmegleSection, Thumbnail
from hmtc.repos.file_repo import create_thumbnail
from hmtc.utils.importer.existing_files import (
    create_omegle_sections,
    import_existing_video_files_to_db,
    import_sections,
)

config = init_config()
STORAGE = Path(config["STORAGE"])


def create_missing_thumbnails():
    images = ImageFile.select().where(ImageFile.id.not_in(Thumbnail.select()))
    for image in images:
        create_thumbnail(Path(image.path), image.id)


@solara.component
def SectionsControls():
    num_sections = OmegleSection.select().count()
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
                    f"Create missing Thumbnails", on_click=create_missing_thumbnails
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
