import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import *
from hmtc.utils.importer.existing_files import import_existing_video_files_to_db

config = init_config()
STORAGE = config["STORAGE"]


@solara.component_vue("./FileCard.vue", vuetify=True)
def FileCard(title: str = "File Card", icon: str = "mdi-account", value: str = "123"):
    pass


def import_files():
    import_existing_video_files_to_db(
        STORAGE / "videos", delete_premigration_superchats=True
    )


@solara.component
def FilesInDatabaseDashboard():
    with solara.Columns([4, 4, 4]):
        FileCard(
            title="Videos", icon="mdi-view-list", value=Video.file_manager.count_all()
        )
        solara.Button(f"Import Videos", on_click=import_files)
        FileCard(title="Albums", icon="mdi-shape", value=Album.file_manager.count_all())
        FileCard(
            title="Tracks", icon="mdi-youtube", value=Track.file_manager.count_all()
        )


@solara.component
def FolderFilesDashboard():
    num_files = solara.use_reactive(0)

    def count_files():
        storage_files = list(STORAGE.glob("**/*"))
        num_files.set(len(storage_files))

    with solara.Columns([4, 4, 4]):

        FileCard(title="Number of Files", icon="mdi-music", value=num_files.value)
        solara.Button("Count Files", on_click=count_files)
        FileCard(title="Artists", icon="mdi-account", value=Artist.repo.count())
        FileCard(title="Users", icon="mdi-account", value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    FilesInDatabaseDashboard()

    FolderFilesDashboard()
