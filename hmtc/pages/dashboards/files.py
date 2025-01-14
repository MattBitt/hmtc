import solara

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import Album, Artist, Channel, Track, User, Video
from hmtc.models import VideoFiles
from hmtc.utils.importer.existing_files import import_existing_video_files_to_db
from hmtc.utils.youtube_functions import download_channel_files
from peewee import fn
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
    import_existing_video_files_to_db(STORAGE / "videos")


def download_channel_files_from_youtube(*args, **kwargs):
    pass


#     for channel in Channel.repo.all():
#         _channel = Channel(channel)
#         files = download_channel_files(channel.youtube_id, channel.url)

#         for file in files:
#             Channel.fm.add_file(_channel, file)


@solara.component
def FilesInDatabaseDashboard():
    num_videos = Video.count()
    info_files = VideoFiles.select(fn.COUNT(VideoFiles.info_id)).where(VideoFiles.info_id.is_null(False)).scalar()
    poster_files = VideoFiles.select(fn.COUNT(VideoFiles.poster_id)).where(VideoFiles.poster_id.is_null(False)).scalar()
    video_files = VideoFiles.select(fn.COUNT(VideoFiles.video_id)).where(VideoFiles.video_id.is_null(False)).scalar()
    audio_files = VideoFiles.select(fn.COUNT(VideoFiles.audio_id)).where(VideoFiles.audio_id.is_null(False)).scalar()
    subtitle_files = VideoFiles.select(fn.COUNT(VideoFiles.subtitle_id)).where(VideoFiles.subtitle_id.is_null(False)).scalar()
    
    total_files = info_files + poster_files + video_files + audio_files + subtitle_files
    with solara.Card(title=f"Source Videos' ({num_videos}) - Files "):
        with solara.Columns():
            FileCard(
                title="Info Files",
                icon="mdi-view-list",
                value=info_files,
                button_caption="Import Video Files",
                event_button_click=import_video_files,
            )
            FileCard(
                title="Posters",
                icon="mdi-view-list",
                value=poster_files,
                button_caption="",
                event_button_click=None,
            )
            FileCard(
                title="Subtitles",
                icon="mdi-view-list",
                value=subtitle_files,
                button_caption="",
                event_button_click=None,
            )
            FileCard(
                title="Video Files",
                icon="mdi-view-list",
                value=video_files,
                button_caption="",
                event_button_click=None,
            )
            FileCard(
                title="Audio Files",
                icon="mdi-view-list",
                value=audio_files,
                button_caption="",
                event_button_click=None,
            )
        FileCard(title="Total", icon="mdi-shape", value=total_files)
    with solara.Columns([6, 6]):
        FileCard(
            title="Channels",
            icon="mdi-youtube",
            value=543,
            event_button_click=download_channel_files_from_youtube,
        )
        # FileCard(title="Tracks", icon="mdi-youtube", value=Track.fm.count_all())


@solara.component
def FolderFilesDashboard():
    solara.Markdown(f"## Files in the Storage Folder")
    num_files = solara.use_reactive(0)

    def count_files():
        counter = 0
        storage_files = STORAGE.glob("**/*")
        for file in storage_files:
            if file.is_file():
                counter += 1
        num_files.set(counter)

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
