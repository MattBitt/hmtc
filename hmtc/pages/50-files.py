import time
from pathlib import Path

import solara
import solara.lab
from loguru import logger

from hmtc.config import init_config
from hmtc.db import import_existing_video_files_to_db
from hmtc.models import File, Video, VideoFile

config = init_config()


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

    video_files = Video.select().join(VideoFile).join(File).distinct()

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
    videos = Video.select().where(Video.enabled == True)
    for video in videos:
        if not video.has_video:
            video.download_video()
            logger.debug("starting sleep")
            time.sleep(10)
            logger.debug("finished sleep")


def extract_missing_audio():
    videos = Video.select().where(Video.enabled == True)
    for video in videos:
        if video.has_video and not video.has_audio:
            video.extract_audio()
            time.sleep(1)


@solara.component
def Page():
    db_files = File.select()

    folder = Path(config.get("PATHS", "MEDIA")) / "sources"
    folder_files = [f for f in folder.rglob("*") if f.is_file()]

    def add_existing_files():
        import_existing_video_files_to_db(folder)

    with solara.ColumnsResponsive(12, large=4):
        DBversusFileCards(db_files, folder_files)

        with solara.Card():
            solara.Button("Add existing files to database", on_click=add_existing_files)
            solara.Button(
                "Download all missing videos", on_click=download_missing_videos
            )
        with solara.Card():
            solara.Button(
                "Extract all missing audio from downloaded videos",
                on_click=extract_missing_audio,
            )
