from pathlib import Path

import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains import Album, Artist, Channel, Track, User, Video
from hmtc.models import (
    AudioFile,
    ChannelFiles,
    ImageFile,
    InfoFile,
    SubtitleFile,
    Thumbnail,
    VideoFile,
    VideoFiles,
)
from hmtc.utils.importer.existing_files import (
    import_channel_files_to_db,
    import_existing_video_files_to_db,
)
from hmtc.utils.youtube_functions import download_channel_files

config = init_config()
STORAGE = Path(config["STORAGE"])
WORKING = Path(config["WORKING"])


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


def process_working():
    for file in WORKING.glob("*___*"):
        yt_id = str(file.stem)[-11:]
        logger.debug(f"Found a file for {yt_id}")
        vid = Video.get_by(youtube_id=yt_id)
        if vid is None:
            logger.error(f"Youtube ID {yt_id} not found in DB. Skipping")
            continue
        else:
            vf = (
                VideoFiles.select()
                .where(VideoFiles.item_id == vid.instance.id)
                .get_or_none()
            )

            if vf.video_id is None and file.suffix == ".mp4":
                logger.debug(f"Found a missing video file. Adding it")
                vid.add_file(file)
            else:
                logger.debug(f"Somethings fish. Investigate before moving")
                logger.debug(f"Vid  = {vid}")
                logger.debug(f"vf = {vf}")

    logger.success(f"Finished processing Working folder")


@solara.component
def WorkingFilesCard():
    with solara.Card(f"Working Files"):
        found_files = []
        for file in WORKING.glob("downloads/*"):
            if file.is_file():
                found_files.append(file)
        solara.Markdown(f"{len(found_files)} found in the Working folder")
        solara.Button(
            f"Process Working Folder", on_click=process_working, classes=["button"]
        )


@solara.component
def VideoFilesCard():
    num_video_files = solara.use_reactive(0)
    extra_files = solara.use_reactive([])

    def count_files():
        counter = 0
        storage_files = (STORAGE / "videos").glob("**/*")
        for file in storage_files:
            if file.is_file():
                counter += 1
        num_video_files.set(counter)

    def find_extra_files():
        # Get all paths from all tables in a single query
        all_db_paths = (
            ImageFile.select(ImageFile.path)
            .union_all(InfoFile.select(InfoFile.path))
            .union_all(SubtitleFile.select(SubtitleFile.path))
            .union_all(AudioFile.select(AudioFile.path))
            .union_all(VideoFile.select(VideoFile.path))
            .union_all(Thumbnail.select(Thumbnail.path))
        )
        db_paths = {str(Path(p.path).resolve()) for p in all_db_paths}

        # Find files on disk that aren't in the database
        found_extra = []
        storage_path = (STORAGE / "videos").resolve()
        for file in storage_path.glob("**/*"):
            if file.is_file():
                normalized_path = str(file.resolve())
                if normalized_path not in db_paths:
                    found_extra.append(file)

        # Update the reactive variable with results
        extra_files.set(found_extra)
        logger.success(f"Found {len(found_extra)} files not in database")
        logger.debug(found_extra)

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

    total_files = (
        info_files + (poster_files * 2) + video_files + audio_files + subtitle_files
    )
    with solara.Card(title=f"Videos ({num_videos})"):

        with solara.Row(justify="center"):
            solara.Markdown(f"## Database")
        with solara.Row(justify="center"):
            solara.Text(f"infos {info_files}", classes=["mx-6"])
            with solara.Column():
                solara.Text(f"posters: {poster_files}", classes=["mx-6"])

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
                        solara.Button(f"Find extra files", on_click=find_extra_files)
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

    total_files = info_files + (poster_files * 2)
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
    WorkingFilesCard()
    VideoFilesCard()
    ChannelFilesCard()
