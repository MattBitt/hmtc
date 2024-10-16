import time
from pathlib import Path

import solara
import solara.lab
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Channel, Playlist, Series
from hmtc.models import File as FileModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import File as FileObject
from hmtc.schemas.file import FileManager

config = init_config()

STORAGE = Path(config["paths"]["storage"])
WORKING = Path(config["paths"]["working"])


def count_types(files):
    num_files = {}
    for file in files:
        try:
            key = file.extension
        except AttributeError:
            key = file.suffix
        if key not in num_files:
            num_files[key] = 0
        num_files[key] += 1
    return num_files


def get_folder_files(folder):
    files = [x for x in list(folder.rglob("*")) if x.is_file()]
    return files


def get_series_files():
    db_files = Series.select().join(FileModel).where(FileModel.series_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "series")
    return db_files, folder_files


def get_playlist_files():
    db_files = (
        Playlist.select().join(FileModel).where(FileModel.playlist_id.is_null(False))
    )
    folder_files = get_folder_files(STORAGE / "playlists")
    return db_files, folder_files


def get_channel_files():
    db_files = (
        Channel.select().join(FileModel).where(FileModel.channel_id.is_null(False))
    )
    folder_files = get_folder_files(STORAGE / "channels")
    return db_files, folder_files


def get_video_files():
    # db_files = VideoModel.select().join(File).where(File.video_id.is_null(False))
    db_files = FileModel.select().where(FileModel.video_id.is_null(False))

    folder_files = get_folder_files(STORAGE / "videos")

    return db_files, folder_files


def FileTypeInfoCard(ftype):
    if ftype == "Series":
        db_files, folder_files = get_series_files()
    elif ftype == "Playlists":
        db_files, folder_files = get_playlist_files()
    elif ftype == "Channels":
        db_files, folder_files = get_channel_files()
    elif ftype == "Videos":
        db_files, folder_files = get_video_files()
    else:
        db_files, folder_files = [], []

    with solara.Card(title=ftype):
        solara.Markdown(f"**{len(db_files)}** files in Database")
        solara.Markdown(f"**{len(folder_files)}** files in Storage Folder")
        solara.Markdown("End of Card")


@solara.component
def Page():
    messages = solara.use_reactive([])
    have_files_not_in_db = solara.use_reactive([])
    files_in_db_not_found = solara.use_reactive([])

    def compare_files_vs_db():
        db_files, folder_files = get_video_files()
        messages.set(
            [
                f"Found {len(db_files)} files in database.",
                f"Found {len(folder_files)} files in storage folder",
            ]
        )
        have_files_not_in_db.set(
            [
                str(x)
                for x in folder_files
                if str(x) not in [y.filename for y in db_files]
            ]
        )
        files_in_db_not_found.set(
            [
                str(x.path + "/" + x.filename)
                for x in db_files
                if x.filename not in [str(y) for y in folder_files]
            ]
        )

        logger.error(f"Files not in DB: {len(have_files_not_in_db.value)}")
        logger.error(f"Files not in Folder: {len(files_in_db_not_found.value)}")

    unique_vids = VideoModel.select(VideoModel.id).where(
        VideoModel.contains_unique_content == True
    )

    files = FileModel.select().where(FileModel.video_id.is_null(False))
    file_tuples = [(x.video_id, x.file_type) for x in files]

    file_types = ["info", "audio", "video", "poster", "album_nfo", "subtitle"]
    missing_files = dict(zip(file_types, [0] * len(file_types)))
    found_files = missing_files.copy()
    for vid in unique_vids:
        for ftype in file_types:
            if (vid.id, ftype) not in file_tuples:
                missing_files[ftype] += 1
            else:
                found_files[ftype] += 1

    logger.error(f"Missing {missing_files} video files")
    logger.error(f"Found {found_files} videos")
    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        ftypes = ["Series", "Channels"]
        with solara.Columns([6, 6]):
            for f in ftypes:
                FileTypeInfoCard(f)
        with solara.Columns([6, 6]):
            with solara.Card():
                with solara.Info():
                    solara.Markdown(f"**{len(unique_vids)}** unique videos")
                    for ftype in file_types:
                        solara.Markdown(
                            f"**{missing_files[ftype]}** missing {ftype} files"
                        )
                    for ftype in file_types:
                        solara.Markdown(f"**{found_files[ftype]}** found {ftype} files")
        with solara.Card():
            solara.Button("Check Files", on_click=compare_files_vs_db)
            for message in messages.value:
                solara.Markdown(f"**{message}**")
        with solara.Columns([6, 6]):
            with solara.Card(title="Files not in DB"):
                for message in have_files_not_in_db.value:
                    solara.Markdown(f"**{message}**")
            with solara.Card(title="Files not in folder"):
                for message in files_in_db_not_found.value:
                    solara.Markdown(f"**{message}**")
