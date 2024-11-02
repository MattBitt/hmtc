import time
from pathlib import Path

import solara
import solara.lab
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import Channel, Playlist, Series
from hmtc.models import File as FileModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel

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


def get_track_files():
    db_files = FileModel.select().where(FileModel.track_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "tracks")
    return db_files, folder_files


def get_album_files():
    db_files = FileModel.select().where(FileModel.album_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "tracks")
    # hack for now
    folder_files = [f for f in folder_files if f.name[:5] == "cover"]
    return db_files, folder_files


@solara.component
def AlbumFilesInfoCard():
    db_files, folder_files = get_album_files()
    albums = AlbumModel.select()
    file_types = ["poster"]

    with solara.Card(title="Albums"):
        solara.Markdown(f"**{len(albums)}** total Albums in DB")
        solara.Markdown(f"**{len(db_files)}** files in Database")
        solara.Markdown(f"**{len(folder_files)}** files in Storage Folder")


def ChannelFilesInfoCard():
    db_files, folder_files = get_channel_files()
    channels = Channel.select()
    with solara.Card(title="Channels"):
        solara.Markdown(f"**{len(channels)}** total Channels in DB")
        solara.Markdown(f"**{len(db_files)}** files in Database")
        solara.Markdown(f"**{len(folder_files)}** files in Storage Folder")


def SeriesFilesInfoCard():
    db_files, folder_files = get_series_files()
    serieses = Series.select()
    with solara.Card(title="Series"):
        solara.Markdown(f"**{len(serieses)}** total Channels in DB")
        solara.Markdown(f"**{len(db_files)}** files in Database")
        solara.Markdown(f"**{len(folder_files)}** files in Storage Folder")


@solara.component
def TrackInfoCard():
    db_files, folder_files = get_track_files()
    tracks = TrackModel.select()
    albums = AlbumModel.select()
    file_types = ["audio", "lyrics", "poster"]

    file_tuples = [(x.track_id, x.file_type) for x in db_files]

    in_db_not_folder = []

    for file in db_files:
        if file.filename not in [x.name for x in folder_files]:
            in_db_not_folder.append(file)

    # existing files that need to be deleted or added to the database
    in_folder_not_db = []
    for file in folder_files:
        # not the best way to do this
        # this is actually an 'album' file
        if file.name[:5] == "cover":
            continue

        if file.name not in [x.filename for x in db_files]:
            in_folder_not_db.append(file)

    missing_files = dict(zip(file_types, [0] * len(file_types)))
    found_files = missing_files.copy()
    for track in tracks:
        for ftype in file_types:
            if (track.id, ftype) not in file_tuples:
                missing_files[ftype] += 1
            else:
                found_files[ftype] += 1

    def delete_file_rows():
        for file in in_db_not_folder:
            file.delete_instance()

    def delete_files_from_disk():
        for file in in_folder_not_db:
            file.unlink()

    with solara.Card(title="Tracks"):
        with solara.Info(label="Tracks"):
            solara.Markdown(f"**{len(tracks)}** tracks")
            solara.Markdown(f"**Missing Files**")
            with solara.Row():
                with solara.ColumnsResponsive():
                    for ftype in file_types:
                        with solara.Card():
                            solara.Markdown(f"**{ftype}**")
                            solara.Markdown(f"**{missing_files[ftype]}**")

        with solara.Card(title="In DB but not folder"):
            if len(in_db_not_folder) == 0:
                with solara.Success("All DB Files accounted for !"):
                    solara.Markdown("You're all set!")
            elif len(in_db_not_folder) > 10:
                with solara.Error("Too many files to list. Showing first 50"):
                    for file in in_db_not_folder[:50]:
                        solara.Markdown(f"**{file.path + '/' + file.filename}**")
            else:
                with solara.Info(f"Files not found on Disk {len(in_db_not_folder)}"):
                    for file in in_db_not_folder:
                        solara.Markdown(f"**{file.path + file.filename}**")
            solara.Button(
                f"Delete All ({len(in_db_not_folder)}) File Rows from the Database",
                on_click=delete_file_rows,
                classes=["button", "mydanger"],
                disabled=len(in_db_not_folder) == 0,
            )

        with solara.Card(title="In Folder but not in DB"):
            if len(in_folder_not_db) == 0:
                with solara.Success("All Folder Files accounted for!"):
                    solara.Markdown("You're all set!")
            elif len(in_folder_not_db) > 10:
                with solara.Error("Too many files to list. Showing first 50"):
                    for file in in_folder_not_db[:50]:
                        solara.Markdown(f"**{file}**")
            else:
                with solara.Info(f"Files not in DB {len(in_folder_not_db)}"):
                    for file in in_folder_not_db:
                        solara.Markdown(f"**{file}**")
            solara.Button(
                f"Delete All ({len(in_folder_not_db)}) Files from the Disk",
                on_click=delete_files_from_disk,
                classes=["button", "mydanger"],
                disabled=len(in_folder_not_db) == 0,
            )


@solara.component
def VideoFilesInfoCard(
    unique_vids=None, file_types=None, missing_files=None, found_files=None
):
    with solara.Info(label="Videos"):
        solara.Markdown(f"**{len(unique_vids)}** unique videos")
        solara.Markdown(f"**Missing Files**")
        with solara.Row():
            with solara.ColumnsResponsive():
                for ftype in file_types:
                    with solara.Card():
                        solara.Markdown(f"**{ftype}**")
                        solara.Markdown(f"**{missing_files[ftype]}**")
    # for ftype in file_types:
    #     solara.Markdown(f"**{found_files[ftype]}** found {ftype} files")


@solara.component
def Page():
    messages = solara.use_reactive([])
    have_files_not_in_db = solara.use_reactive([])
    files_in_db_not_found = solara.use_reactive([])

    unique_vids = VideoModel.select(VideoModel.id).where(
        VideoModel.contains_unique_content == True
    )

    files = FileModel.select().where(FileModel.video_id.is_null(False))
    file_tuples = [(x.video_id, x.file_type) for x in files]

    # need to standardize this
    file_types = ["info", "audio", "video", "poster", "album_nfo", "subtitle"]
    missing_files = dict(zip(file_types, [0] * len(file_types)))
    found_files = missing_files.copy()
    for vid in unique_vids:
        for ftype in file_types:
            if (vid.id, ftype) not in file_tuples:
                missing_files[ftype] += 1
            else:
                found_files[ftype] += 1

    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        with solara.Card():
            AlbumFilesInfoCard()
        with solara.Card():
            SeriesFilesInfoCard()
        with solara.Card():
            ChannelFilesInfoCard()

        with solara.Card():
            VideoFilesInfoCard(
                unique_vids=unique_vids,
                file_types=file_types,
                missing_files=missing_files,
                found_files=found_files,
            )
        with solara.Card():
            TrackInfoCard()
