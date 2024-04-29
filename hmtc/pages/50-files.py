import solara
import solara.lab
from pathlib import Path
from hmtc.models import File, Video, VideoFile
from hmtc.config import init_config
import time
from loguru import logger
from hmtc.db import import_existing_video_files_to_db

from hmtc.pages import config


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

    with solara.Card(title="Files in db"):

        solara.Markdown(f"**{len(db)} files in db**")
        for key, num in enumerate(sorted(folder_files_type_counts)):
            solara.Markdown(f"**{num}** files: {folder_files_type_counts[num]}")

    with solara.Card(title="Files in Folder"):

        solara.Markdown(f"**{len(folder)}** files in folder and subfolders")

        for key, num in enumerate(sorted(db_files_type_counts)):
            if num:
                solara.Markdown(f"**{num}** files: {db_files_type_counts[num]}")


@solara.component
def DBversusFileCards(db_files, folder_files):
    db_files_list = {Path(file.local_path, file.filename) for file in db_files}
    folder_files_list = {file for file in folder_files}

    diff = db_files_list.symmetric_difference(folder_files_list)
    video_files = Video.select().join(VideoFile).join(File).distinct()

    def file_diffs():
        logger.debug("Running File Tests")

    solara.Button("Compare Files in Folder vs DB", on_click=file_diffs)
    if len(diff) == 0:
        solara.Markdown("No differences in files vs Database")
        return

    FileTypesCard(db_files_list, folder_files_list)

    with solara.Card():

        diff_file_counts = {}
        for file in diff:
            diff_file_counts[file.suffix] = diff_file_counts.get(file.suffix, 0) + 1
        solara.Markdown(f"**{len(diff)}** files that DONT exist in (db AND folder)")
        if len(diff) < 10:
            for file in diff:
                solara.Markdown(f"**{file}**")

        for ext in diff_file_counts:
            solara.Markdown(f"**{diff_file_counts[ext]}** files: {ext}")

    with solara.Card(title="Files in Database (not in Folder)"):

        diff = db_files_list - folder_files_list
        if len(diff) < 10:
            for file in diff:
                solara.Markdown(f"**{file}**")
        else:
            solara.Markdown(f"**{len(diff)}** files in db but not in folder")

    with solara.Card(title="Files in folder not in db"):
        diff = folder_files_list - db_files_list
        solara.Markdown(f"**{len(diff)}** files in folder but not in db")


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

    folder = Path(config.get("MEDIA", "VIDEO_PATH"))
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
