from pathlib import Path

import peewee
import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.components.file_drop_card import FileInfo
from hmtc.config import init_config
from hmtc.models import Section, Video
from hmtc.utils.section_manager import SectionManager

all_videos = [c.title for c in Video.select()]
if all_videos == []:
    all_videos = ["No Videos"]
time_cursor = solara.reactive(0)

title = solara.reactive("")
url = solara.reactive("http://www.youtube.com")
enabled = solara.reactive(True)
last_update_completed = solara.reactive(None)
contains_unique_content = solara.reactive(False)
youtube_id = solara.reactive(False)

section_list = solara.reactive(None)


config = init_config()

UPLOAD_PATH = Path(config["paths"]["working"]) / "uploads"


def update_videos():
    videos = Video.select()
    for video in videos:
        logger.debug("Checking for new videos in video: {}", video.title)
        video.check_for_new_videos()


def update_all():
    logger.debug("Updating")
    for p in Video.select().where(Video.enabled == True):
        p.check_for_new_videos()
    logger.success("Updated all videos")


def add_new_video():
    try:
        video = Video.create(
            title="New Video",
            url="http://www.youtube.com",
            youtube_id="adsuoibgvpfrjdlk;af",
            enabled=True,
            last_update_completed=None,
        )

        logger.debug(f"Created new video: {video.title}")
    except peewee.IntegrityError:
        logger.debug("Video already exists")
        return


def save_video(video):
    video.title = title.value
    video.url = url.value
    video.enabled = True
    video.save()
    logger.success(f"Added new video {video.title}")


def write_to_disk(file: FileInfo):
    logger.debug(f"Writing file to disk: {file['name']}")

    with open(UPLOAD_PATH / file["name"], "wb") as src_file:
        src_file.write(file["data"])

    return file["name"]


def VideoDetail(video_id):
    video = Video.select().join(Section).where(Video.id == video_id).get_or_none()
    if video is None:
        return solara.Markdown("No Video Found")
    sm = SectionManager(video)
    section_list.set(video.sections)
    title.set(video.title)
    url.set(video.url)
    enabled.set(video.enabled)
    contains_unique_content.set(video.contains_unique_content)
    youtube_id.set(video.youtube_id)

    @task
    def download_video():
        logger.debug(f"Downloading video asyncly? {video.title}")
        video.download_video()

    def add_section():
        logger.debug(f"Adding section {time_cursor.value} to video {video.title}")
        sm.split_section_at(time_cursor.value)
        logger.debug(f"Updating: {video.title}")
        logger.debug("Finished adding section")

    def update_video():
        save_video(video)
        logger.success(f"Updated video {video.title}")

    if video.title is None:
        with solara.Card():
            solara.InputText(label="Title", value=youtube_id, continuous_update=False)
            solara.Button(
                label="Refresh from Youtube", on_click=lambda: video.update_from_yt()
            )
    else:
        with solara.ColumnsResponsive(12, large=6):
            with solara.Column():
                if video.poster is not None:
                    solara.Image(video.poster, width="300px")
                solara.InputText(label="Name", value=title, continuous_update=False)
                solara.Markdown(f"Youtube ID: {video.youtube_id}")
                if video.episode is not None:
                    solara.Markdown(f"Episode: {video.episode}")
                solara.Markdown(f"Sections: {video.sections.count()}")
                solara.Markdown(f"Duration: {video.duration}")
                solara.Checkbox(label="Enabled", value=enabled)
                solara.Checkbox(label="Unique", value=contains_unique_content)
                solara.Markdown("## Files")
                for vf in video.files:
                    with solara.Row():
                        solara.Markdown(f"**File**: {vf.filename + vf.extension}")
                        solara.Button(
                            label="Delete",
                            on_click=lambda: vf.delete_instance(),
                        )
                with solara.Row():
                    solara.Button(label="Save", on_click=update_video)
                    solara.Button(label="Download Video", on_click=download_video)
                    solara.Button(
                        label="Extract Audio", on_click=lambda: video.extract_audio()
                    )

            with solara.Column():
                solara.Markdown("## Sections")
                solara.InputText("Timestamp", value=time_cursor)
                solara.Button(
                    "Add section at timestamp",
                    on_click=add_section,
                )

                for sect in section_list.value:
                    with solara.Card(f"ID: {sect.id}"):
                        solara.Markdown(f"Start:{sect.start} End:{sect.end}")
                        solara.Markdown(f"Previous section: {sect.previous_section}")
                        solara.Markdown(f"Next section: {sect.next_section}")


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        return
    video_id = router.parts[level:][0]
    if video_id.isdigit():
        VideoDetail(video_id)


# @solara.component
# def VideoDetail(video):
#     solara.Markdown(f"***This is the Detail Section for {video.title}!!!!***")
#     solara.Markdown(f"**Youtube_ID: {video.youtube_id}")

#     if video.poster:
#         solara.Image(video.poster, width="400px")
#     with solara.Column():

#         solara.Markdown(f"**Sections**: {video.sections.count()}")
#         solara.Markdown(f"**Files**: {video.files.count()}")

#         solara.Markdown(f"**Duration**: {video.duration}")
#         solara.Button(
#             "Refresh video Info",
#             on_click=lambda: video.update_from_yt(),
#         )
#         solara.Button(
#             "Download video File",
#             on_click=lambda: video.download_video(),
#         )
#         solara.Button("Extract Audio", on_click=lambda: video.value.extract_audio())

#     solara.Markdown("## Files")
#     for vf in video.files:
#         with solara.Column():
#             solara.Markdown(f"**File**: {vf.filename + vf.extension}")


# def get_url_id_argument(router, level):
#     try:
#         return router.parts[level:][0]
#     except Exception as e:
#         raise e


# @solara.component
# def VideoDetailPage(video_id):

#     @task
#     def grab_video(video_id):

#         this_video = Video.get(id=video_id)
#         time.sleep(10)
#         video.set(this_video)

#     if loading.value is True:
#         grab_video(video_id)
#         solara.SpinnerSolara(size="100px")
#     else:

#         with solara.Card():
#             solara.Markdown(f"Current Loading State {loading.value}")
#             if video.value.title is None:
#                 solara.Markdown("No Infomation Found for this video")
#                 solara.Button(
#                     "Refresh Video Info", on_click=lambda: video.value.update_from_yt()
#                 )
#             else:
#                 VideoDetail(video.value)


# @solara.component
# def Page():

#     router = solara.use_router()
#     level = solara.use_route_level()
#     video_id = get_url_id_argument(router, level)
#     if video_id is None:
#         return solara.Markdown("No Video ID Found")
#     logger.debug("Video ID from URL: ", video_id)
#     VideoDetailPage(video_id)
