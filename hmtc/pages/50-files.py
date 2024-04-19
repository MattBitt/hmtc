import solara
import solara.lab
from pathlib import Path
from hmtc.models import File, Video, VideoFile
from hmtc.config import init_config
import time
from loguru import logger

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


def DBversusFileCards(db_files, folder_files):
    db_files_list = {Path(file.local_path, file.filename) for file in db_files}
    folder_files_list = {file for file in folder_files}

    diff = db_files_list.symmetric_difference(folder_files_list)
    video_files = Video.select().join(VideoFile).join(File).distinct()

    def file_diffs():
        logger.debug("Running File Tests")

    if len(diff) == 0:
        solara.Markdown("No differences in files vs Database")
        solara.Button("Run File Tests Anyway", on_click=file_diffs)
        return

    db_files_type_counts = count_types(db_files)
    folder_files_type_counts = count_types(folder_files)

    with solara.Card():

        diff_file_counts = {}
        for file in diff:
            diff_file_counts[file.suffix] = diff_file_counts.get(file.suffix, 0) + 1

        solara.Markdown(f"**{len(diff)}** files that don't exist in both db and folder")
        for ext in diff_file_counts:
            solara.Markdown(f"**{diff_file_counts[ext]}** files: {ext}")

    with solara.Card(title="Files in db"):

        files = db_files
        solara.Markdown(f"**{len(db_files_list)} files in db**")
        for key, num in enumerate(sorted(folder_files_type_counts)):
            solara.Markdown(f"**{num}** files: {folder_files_type_counts[num]}")

    with solara.Card(title="Files in Database"):
        folder = Path(config.get("MEDIA", "VIDEO_PATH"))
        files = folder_files
        solara.Markdown(f"**{len(files)}** files in folder and subfolders")

        for key, num in enumerate(sorted(db_files_type_counts)):
            if num:
                solara.Markdown(f"**{num}** files: {db_files_type_counts[num]}")

    with solara.Card(title="Files in Folder (not in DB)"):

        diff = db_files_list - folder_files_list
        solara.Markdown(f"**{len(diff)}** files in db but not in folder")

    with solara.Card(title="Files in folder not in db"):
        diff = folder_files_list - db_files_list
        solara.Markdown(f"**{len(diff)}** files in folder but not in db")

    with solara.Card(title="Video Files (not video files)"):
        solara.Markdown(f"**{video_files.count()}** video file associations in db")
        max_files = 0
        vid = None
        same_length = 0
        for video in video_files:
            if len(video.files) > max_files:
                max_files = len(video.files)
                vid = video
        solara.Markdown(f"Video {vid} had the most files: {max_files}")
        solara.Markdown("Files")
        with solara.Column():
            for v in vid.files:
                solara.Markdown(f"**{v.file.filename}**")


def download_missing_videos():
    videos = Video.select().where(Video.enabled == True)
    for video in videos:
        if not video.has_video:
            video.download_video()
            time.sleep(10)


@solara.component
def FileTypesCard():
    with solara.Card():
        solara.Markdown("Video Files")
        have_video = 0

        videos = Video.select().where(Video.enabled == True)
        total = videos.count()
        for vid in videos:
            if vid.has_video:
                have_video += 1
        solara.Markdown(f"**{have_video}** videos have a 'video' file")
        solara.Markdown(f"**{total - have_video}** videos DONT have a 'video' file")


@solara.component
def Page():
    db_files = File.select()

    folder = Path(config.get("MEDIA", "VIDEO_PATH"))
    folder_files = [f for f in folder.rglob("*") if f.is_file()]

    with solara.ColumnsResponsive(12, large=4):
        DBversusFileCards(db_files, folder_files)

        with solara.Card():
            solara.Button(
                "Download all missing videos", on_click=download_missing_videos
            )

        FileTypesCard()
