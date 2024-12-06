import time
from pathlib import Path

import solara
import solara.lab
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Album as AlbumModel
from hmtc.models import Channel, Series
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


def get_album_and_track_files():
    db_files = FileModel.select().where(FileModel.track_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "tracks")
    return db_files, folder_files


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
def DBvsFolderFilesInfoCard():

    def delete_file_rows():
        # for file in in_db_not_folder:
        #     file.delete_instance()
        pass

    def delete_files_from_disk():
        # for file in in_folder_not_db:
        #     file.unlink()
        pass

    folder_files = get_folder_files(STORAGE)
    folder_file_tuples = [(str(x.parent), x.name) for x in folder_files]
    db_files = FileModel.select(FileModel.path, FileModel.filename)

    db_file_tuples = [(x.path, x.filename) for x in db_files]

    in_db_not_folder = []
    in_folder_not_db = []
    found1_counter = 0
    found2_counter = 0
    for file in db_files:
        if (file.path, file.filename) not in folder_file_tuples:
            in_db_not_folder.append(file)
        else:
            found1_counter += 1

    for file in folder_file_tuples:
        if (file[0], file[1]) not in db_file_tuples:
            in_folder_not_db.append(file)
        else:
            found2_counter += 1
    logger.debug(f"Found {found1_counter} in DB and also in folder")
    logger.debug(f"Found {found2_counter} in folder and also in DB")

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
def AlbumAndTrackFilesInfoCard():
    albums = AlbumModel.select(AlbumModel.id)
    tracks = TrackModel.select(TrackModel.id)
    album_db_files = FileModel.select(FileModel).where(
        FileModel.album_id.is_null(False)
    )
    track_db_files = FileModel.select(FileModel).where(
        FileModel.track_id.is_null(False)
    )

    album_file_types = ["poster"]
    album_file_tuples = [(x.album_id, x.file_type) for x in album_db_files]
    album_missing_files = dict(zip(album_file_types, [0] * len(album_file_types)))
    for album in albums:
        for ftype in album_file_types:
            if (album.id, ftype) not in album_file_tuples:
                album_missing_files[ftype] += 1

    track_file_types = ["audio", "lyrics"]
    track_file_tuples = [(x.track_id, x.file_type) for x in track_db_files]
    track_missing_files = dict(zip(track_file_types, [0] * len(track_file_types)))
    for track in tracks:
        for ftype in track_file_types:
            if (track.id, ftype) not in track_file_tuples:
                track_missing_files[ftype] += 1

    with solara.Row():
        with solara.Columns([6, 6]):
            with solara.Card():
                solara.Markdown(f"## Albums: {len(albums)}")
                solara.Markdown(f"### Files in Database: {len(album_db_files)}")
                with solara.Row():
                    with solara.ColumnsResponsive():
                        for ftype in album_file_types:
                            with solara.Card():
                                if album_missing_files[ftype] > 0:
                                    with solara.Error():
                                        solara.Markdown(f"**Albums Missing {ftype}**")
                                        solara.Markdown(
                                            f"**{album_missing_files[ftype]}/{len(albums)}** ({album_missing_files[ftype] / len(albums) * 100:.2f}%)"
                                        )
                                        with solara.Link(
                                            f"/albums/missing-files/{ftype}"
                                        ):
                                            solara.Button(f"View", classes=["button"])
                                else:
                                    with solara.Success():
                                        solara.Markdown(f"**Album {ftype}**")
                                        solara.Markdown(f"**0**")
            with solara.Card():
                solara.Markdown(f"## Tracks: {len(tracks)}")
                solara.Markdown(f"### Files in Database: {len(track_db_files)}")
                with solara.Row():
                    with solara.ColumnsResponsive():
                        for ftype in track_file_types:
                            with solara.Card():
                                if track_missing_files[ftype] > 0:
                                    with solara.Error():
                                        solara.Markdown(f"**Tracks Missing {ftype}**")
                                        solara.Markdown(
                                            f"**{track_missing_files[ftype]}/{len(tracks)}** ({track_missing_files[ftype] / len(tracks) * 100:.2f}%)"
                                        )
                                        with solara.Link(
                                            f"/tracks/missing-files/{ftype}"
                                        ):
                                            solara.Button(f"View", classes=["button"])
                                else:
                                    with solara.Success():
                                        solara.Markdown(f"**Track {ftype}**")
                                        solara.Markdown(f"**0**")


@solara.component
def VideoFilesInfoCard():
    unique_vids = VideoModel.select(VideoModel.id).where(
        VideoModel.contains_unique_content == True
    )

    files = FileModel.select().where(FileModel.video_id.is_null(False))
    file_tuples = [(x.video_id, x.file_type) for x in files]

    # need to standardize this
    file_types = ["info", "audio", "video", "poster", "album_nfo", "subtitle"]
    missing_files = dict(zip(file_types, [0] * len(file_types)))

    for vid in unique_vids:
        for ftype in file_types:
            if (vid.id, ftype) not in file_tuples:
                missing_files[ftype] += 1
    logger.debug(missing_files)

    solara.Markdown(f"**{len(unique_vids)}** unique videos")
    solara.Markdown(f"**Videos Missing Files**")
    with solara.Row():
        with solara.ColumnsResponsive():
            for ftype in file_types:
                with solara.Card():
                    if missing_files[ftype] > 0:
                        with solara.Error():
                            solara.Markdown(f"**{ftype}**")
                            solara.Markdown(
                                f"**{missing_files[ftype]}** ({missing_files[ftype] / len(unique_vids) * 100:.2f}%)"
                            )
                            with solara.Link(f"/videos/missing-files/{ftype}"):
                                solara.Button(f"View", classes=["button"])
                    else:
                        with solara.Success():
                            solara.Markdown(f"**{ftype}**")
                            solara.Markdown(f"**0**")


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Files Panel")
        solara.Markdown(f"Deprecate me please!")
        return
        with solara.Card(title="Video Files"):
            VideoFilesInfoCard()
        with solara.Card(title="Album and Track Files"):
            AlbumAndTrackFilesInfoCard()
        with solara.Card(title="Series Files"):
            SeriesFilesInfoCard()
        with solara.Card(title="Channel Files"):
            ChannelFilesInfoCard()
        with solara.Card(title="DB vs Folder Files"):
            DBvsFolderFilesInfoCard()
