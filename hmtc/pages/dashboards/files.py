import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import Album, Artist, Channel, Track, User, Video
from hmtc.utils.importer.existing_files import import_existing_video_files_to_db
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = config["STORAGE"]


@solara.component_vue("./FileCard.vue", vuetify=True)
def FileCard(
    title: str = "File Card",
    icon: str = "mdi-account",
    value: str = "123",
    button_caption="",
    event_button_click=None,
):
    pass


def import_video_files(*args, **kwargs):
    import_existing_video_files_to_db(
        STORAGE / "videos", delete_premigration_superchats=True
    )


def download_channel_files_from_youtube(*args, **kwargs):
    for channel in Channel.repo.all():
        _channel = Channel(channel)
        files = download_channel_files(channel.youtube_id, channel.url)

        for file in files:
            Channel.fm.add_file(_channel, file)


@solara.component
def FilesInDatabaseDashboard():
    solara.Markdown(f"## Files in Database")
    with solara.Columns([6, 6]):
        FileCard(
            title="Videos",
            icon="mdi-view-list",
            value=Video.fm.count(),
            button_caption="Import Video Files",
            event_button_click=import_video_files,
        )
        # FileCard(title="Albums", icon="mdi-shape", value=Album.fm.count())
    with solara.Columns([6, 6]):
        FileCard(
            title="Channels",
            icon="mdi-youtube",
            value=Channel.fm.count(),
            event_button_click=download_channel_files_from_youtube,
        )
        # FileCard(title="Tracks", icon="mdi-youtube", value=Track.fm.count_all())


@solara.component
def FolderFilesDashboard():
    solara.Markdown(f"## Files in the Storage Folder")
    num_files = solara.use_reactive(0)

    def count_files():
        storage_files = list(STORAGE.glob("**/*"))
        num_files.set(len(storage_files))

    with solara.Columns([4, 4, 4]):

        FileCard(title="# of Files", icon="mdi-music", value=num_files.value)
        solara.Button("Count Files", on_click=count_files)
        FileCard(title="Artists", icon="mdi-account", value=Artist.repo.count())
        FileCard(title="Users", icon="mdi-account", value=User.repo.count())


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    FilesInDatabaseDashboard()

    FolderFilesDashboard()
