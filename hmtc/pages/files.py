import time
from pathlib import Path

import solara
import solara.lab
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import Channel, File, Playlist, Series, Video as VideoModel
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


@solara.component
def FileTypesCard(db, folder):
    db_files_type_counts = count_types(db)
    folder_files_type_counts = count_types(folder)

    with solara.Card(title="All Files"):
        with solara.ColumnsResponsive(12, large=6):
            with solara.Card(title="Files in Database"):
                solara.Markdown(f"**{len(db)} files**")
                for key, num in enumerate(sorted(db_files_type_counts)):
                    if num:
                        solara.Markdown(f"**{num}** files: {db_files_type_counts[num]}")

            with solara.Card(title="Files in Folder"):
                solara.Markdown(f"**{len(folder)}** files in folder and subfolders")
                for key, num in enumerate(sorted(folder_files_type_counts)):
                    solara.Markdown(f"**{num}** files: {folder_files_type_counts[num]}")


@solara.component
def DBversusFileCards(db_files, folder_files):
    db_files_list = {Path(file.local_path, file.filename) for file in db_files}
    folder_files_list = {file for file in folder_files}
    logger.error("This function is disabled")
    # video_files = Video.select().join(VideoFile).join(File).distinct()

    def missing_files():
        # i don't think order matters here
        return db_files_list.symmetric_difference(folder_files_list)

    missing = missing_files()

    if len(missing) == 0:
        solara.Markdown("Horray! No differences found!")
        return
    solara.Markdown("")
    with solara.Card(title="File Issues"):
        solara.Markdown(
            f"**{len(missing)}** files that are not in BOTH db and folder (not sure which)"
        )

    FileTypesCard(db_files_list, folder_files_list)

    # with solara.Card():

    #     diff_file_counts = {}
    #     for file in d1:
    #         diff_file_counts[file.suffix] = diff_file_counts.get(file.suffix, 0) + 1
    #     solara.Markdown(f"**{len(d1)}** files that DONT exist in (db AND folder)")
    #     if len(d1) < 10:
    #         for file in diff:
    #             solara.Markdown(f"**{file}**")

    #     for ext in diff_file_counts:
    #         solara.Markdown(f"**{diff_file_counts[ext]}** files: {ext}")

    # with solara.Card(title="Files in Database (not in Folder)"):

    #     diff = db_files_list - folder_files_list
    #     if len(diff) < 10:
    #         for file in diff:
    #             solara.Markdown(f"**{file}**")
    #     else:
    #         solara.Markdown(f"**{len(diff)}** files in db but not in folder")

    # with solara.Card(title="Files in folder not in db"):
    #     diff = folder_files_list - db_files_list
    #     solara.Markdown(f"**{len(diff)}** files in folder but not in db")


def download_missing_videos():
    videos = VideoModel.select().where(VideoModel.enabled == True)
    for video in videos:
        if not video.has_video:
            video.download_video()
            logger.debug("starting sleep")
            time.sleep(10)
            logger.debug("finished sleep")


def extract_missing_audio():
    videos = VideoModel.select().where(VideoModel.enabled == True)
    for video in videos:
        if video.has_video and not video.has_audio:
            video.extract_audio()
            time.sleep(1)


def get_folder_files(folder):
    files = [x for x in list(folder.rglob("*")) if x.is_file()]
    return files


def get_series_files():
    db_files = Series.select().join(File).where(File.series_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "series")
    return db_files, folder_files


def get_playlist_files():
    db_files = Playlist.select().join(File).where(File.playlist_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "playlists")
    return db_files, folder_files


def get_channel_files():
    db_files = Channel.select().join(File).where(File.channel_id.is_null(False))
    folder_files = get_folder_files(STORAGE / "channels")
    return db_files, folder_files


def get_video_files():
    db_files = VideoModel.select().join(File).where(File.video_id.is_null(False))
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
def FileTypeCards():
    ftypes = ["Series", "Playlists", "Channels", "Videos"]
    for f in ftypes:
        FileTypeInfoCard(f)


@solara.component
def Page():
    def add_existing_files():
        logger.error("deprecate me!!!")
        # import_existing_video_files_to_db(folder)

    def add_file(*args):
        logger.debug(f"This is only for testing 🤠🤠🤠🤠🤠Adding file to video {args}")
        file = STORAGE / "videos" / "test.info.json"
        f = FileObject.from_path(file)
        video = VideoModel.get(VideoModel.id == 1)
        FileManager.add_file_to_video(f, video)

    MySidebar(router=solara.use_router())
    with solara.Column(classes=["main-container"]):
        with solara.Row():
            solara.Button("Add File to a Video", on_click=add_file)
        with solara.ColumnsResponsive(12, large=4):
            FileTypeCards()

        with solara.Card():
            solara.Button(
                "Add existing files to database",
                on_click=add_existing_files,
                disabled=True,
            )
            solara.Button(
                "Download all missing videos",
                on_click=download_missing_videos,
                disabled=True,
            )
            solara.Button(
                "Extract all missing audio from downloaded videos",
                on_click=extract_missing_audio,
                disabled=True,
            )
