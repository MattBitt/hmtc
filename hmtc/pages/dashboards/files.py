import solara
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import Album, Artist, Channel, Track, User, Video
from hmtc.models import ChannelFiles, Thumbnail, VideoFiles
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
    import_existing_video_files_to_db(STORAGE / "videos")


def download_channel_files_from_youtube(*args, **kwargs):

    for channel in Channel.repo.all():
        _channel = Channel(channel)
        files = download_channel_files(channel.youtube_id, channel.url)

        for file in files:
            Channel.add_file(_channel, file)


@solara.component
def VideoFilesCard():
    num_video_files = solara.use_reactive(0)

    def count_files():
        counter = 0
        storage_files = (STORAGE / "videos").glob("**/*")
        for file in storage_files:
            if file.is_file():
                counter += 1
        num_video_files.set(counter)

    num_videos = Video.count()
    info_files = (
        VideoFiles.select(fn.COUNT(VideoFiles.info_id))
        .where(VideoFiles.info_id.is_null(False))
        .scalar()
    )
    poster_files = (
        VideoFiles.select(fn.COUNT(VideoFiles.poster_id))
        .where(VideoFiles.poster_id.is_null(False))
        .scalar()
    )
    video_files = (
        VideoFiles.select(fn.COUNT(VideoFiles.video_id))
        .where(VideoFiles.video_id.is_null(False))
        .scalar()
    )
    audio_files = (
        VideoFiles.select(fn.COUNT(VideoFiles.audio_id))
        .where(VideoFiles.audio_id.is_null(False))
        .scalar()
    )
    subtitle_files = (
        VideoFiles.select(fn.COUNT(VideoFiles.subtitle_id))
        .where(VideoFiles.subtitle_id.is_null(False))
        .scalar()
    )
    thumbnail_files = (
        Thumbnail.select(fn.COUNT(Thumbnail.id))
        .where(Thumbnail.id.is_null(False))
        .scalar()
    )

    total_files = (
        info_files
        + poster_files
        + video_files
        + audio_files
        + subtitle_files
        + thumbnail_files
    )
    with solara.Card(title=f"Videos ({num_videos})"):

        with solara.Row(justify="center"):
            solara.Markdown(f"## Database")
        with solara.Row(justify="center"):
            solara.Text(f"infos {info_files}", classes=["mx-6"])
            with solara.Column():
                solara.Text(f"posters: {poster_files}", classes=["mx-6"])
                solara.Text(f"thumbs: {thumbnail_files}", classes=["mx-6"])

            solara.Text(f"subtitle {subtitle_files}", classes=["mx-6"])
            solara.Text(f"videos {video_files}", classes=["mx-6"])
            solara.Text(f"audios Files {audio_files}", classes=["mx-6"])
            solara.Text(f"Total {total_files}", classes=["mx-6"])

        with solara.Row(justify="center"):
            with solara.Columns([6, 6]):
                with solara.Column():
                    solara.Markdown(f"## Filesystem")
                    with solara.Row():
                        solara.Button(
                            f"Count Files", on_click=count_files, classes=["button"]
                        )
                        if num_video_files.value > 0:
                            solara.Text(f"{num_video_files.value}", classes=["mx-6"])

                with solara.Column():
                    delta = num_video_files.value - total_files
                    if delta == 0:
                        c = ["success"]
                    else:
                        c = ["warning"]
                    if num_video_files.value > 0:
                        solara.Markdown(f"## Delta")
                        solara.Text(f"{delta}", classes=["mx-6"] + c)


@solara.component
def ChannelFilesCard():
    num_channel_files = solara.use_reactive(0)

    def count_files():
        counter = 0
        storage_files = (STORAGE / "channels").glob("**/*")
        for file in storage_files:
            if file.is_file():
                counter += 1
        num_channel_files.set(counter)

    num_channels = Channel.count()
    info_files = (
        ChannelFiles.select(fn.COUNT(ChannelFiles.info_id))
        .where(ChannelFiles.info_id.is_null(False))
        .scalar()
    )
    poster_files = (
        ChannelFiles.select(fn.COUNT(ChannelFiles.poster_id))
        .where(ChannelFiles.poster_id.is_null(False))
        .scalar()
    )

    total_files = info_files + poster_files
    with solara.Card(title=f"Channels ({num_channels})"):
        with solara.Columns([8, 2, 2]):
            with solara.Column():
                with solara.Row(justify="center"):
                    solara.Markdown(f"## Database")
                with solara.Row():
                    solara.Text(f"Info Files {info_files}", classes=["mx-6"])
                with solara.Column():
                    solara.Text(f"posters: {poster_files}", classes=["mx-6"])
                    solara.Text(f"Total {total_files}", classes=["mx-6"])
                    solara.Button(
                        f"Download Files",
                        on_click=download_channel_files_from_youtube,
                        classes=["button"],
                    )
            with solara.Column():
                with solara.Row(justify="center"):
                    solara.Markdown(f"## Filesystem")
                with solara.Row():
                    solara.Button(
                        f"Count Files", on_click=count_files, classes=["button"]
                    )
                    if num_channel_files.value > 0:
                        solara.Text(f"{num_channel_files.value}", classes=["mx-6"])
            with solara.Column():
                with solara.Row(justify="center"):
                    solara.Markdown(f"## Delta")
                with solara.Row(justify="center"):
                    if num_channel_files.value > 0:
                        delta = num_channel_files.value - total_files
                        if delta == 0:
                            c = ["success"]
                        else:
                            c = ["warning"]

                        solara.Text(f"{delta}", classes=["mx-6"] + c)


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    VideoFilesCard()
    ChannelFilesCard()
