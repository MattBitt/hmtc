import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import *

config = init_config()
STORAGE = config["STORAGE"]


@solara.component_vue("./DomainCard.vue", vuetify=True)
def DomainCard(title: str = "File Card", icon: str = "mdi-account", value: str = "123"):
    pass


@solara.component
def FilesInDatabaseDashboard():
    with solara.Columns([4, 4, 4]):
        DomainCard(title="Channels", icon="mdi-view-list", value=Channel.repo.count())
        DomainCard(title="Series", icon="mdi-shape", value=Series.repo.count())
        DomainCard(
            title="Youtube Series", icon="mdi-youtube", value=YoutubeSeries.repo.count()
        )


@solara.component
def FolderFilesDashboard():
    num_files = solara.use_reactive(0)

    def count_files():
        storage_files = list(STORAGE.glob("**/*"))
        num_files.set(len(storage_files))

    with solara.Columns([4, 4, 4]):

        DomainCard(title="Number of Files", icon="mdi-music", value=num_files.value)
        solara.Button("Count Files", on_click=count_files)
        DomainCard(title="Artists", icon="mdi-account", value=Artist.repo.count())
        DomainCard(title="Users", icon="mdi-account", value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    FilesInDatabaseDashboard()

    FolderFilesDashboard()
