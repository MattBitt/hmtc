from pathlib import Path

import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.domains.channel import Channel
from hmtc.domains.video import Video
from hmtc.models import ImageFile, OmegleSection, Thumbnail, VideoFiles
from hmtc.models import SubtitleFile as SubtitleFileModel
from hmtc.models import Video as VideoModel
from hmtc.utils.importer.existing_files import (
    create_omegle_sections,
    create_video_from_folder,
    import_channel_files_to_db,
    import_existing_video_files_to_db,
    import_sections,
)
from hmtc.utils.subtitles import convert_vtt_to_srt
from hmtc.utils.youtube_functions import (
    download_video_file,
    fetch_ids_from,
    get_video_info,
)

config = init_config()
STORAGE = Path(config["STORAGE"])
WORKING = Path(config["WORKING"])


def download_unique():
    vids_missing_video = VideoFiles.select().where(VideoFiles.video_id.is_null())
    vids_missing_list = set([x.item_id for x in vids_missing_video])

    unique_vids = VideoModel.select(VideoModel.id).where(
        VideoModel.unique_content == True
    )
    unique_list = set([x.id for x in unique_vids])
    to_process = unique_list.intersection(vids_missing_list)
    downloaded = 0
    logger.debug(
        f"Found {len(to_process)} unique videos missing a video file. Downloading"
    )
    for vid_id in to_process:
        video = Video(vid_id)
        download_video_file(
            video.instance.youtube_id, WORKING / video.instance.youtube_id
        )
        downloaded += 1
        logger.debug(
            f"Downloaded {downloaded} videos. {len(to_process) - downloaded} to go"
        )
        if downloaded >= 1000:
            break


def convert_vtts_to_srts():
    vtts = SubtitleFileModel.select().where(SubtitleFileModel.path.contains(".en.vtt"))
    for vtt in vtts:
        new_file_name = vtt.path.replace(".en.vtt", ".srt")
        old_file = Path(vtt.path)
        converted = convert_vtt_to_srt(vtt.path, new_file_name)
        if converted is None:
            logger.error(f"Error converting {vtt}")
            return
        new_file = Path(converted)
        if not new_file.exists():
            logger.error(f"{converted} doesn't exist. keeping {vtt} for now")
            return
        vtt.path = converted
        vtt.save()

        old_file.unlink()


def refresh_from_youtube():

    for channel in Channel.to_auto_update():
        logger.debug(f"Checking channel {channel}")
        not_in_db = []
        ids = fetch_ids_from(channel)
        for youtube_id in ids:
            vid = Video.get_by(youtube_id=youtube_id)
            if vid is None:
                not_in_db.append(youtube_id)

        logger.debug(f"Found {len(ids)} videos at {channel}")
        logger.debug(f"{len(not_in_db)} of them need to be added.")
        if config["general"]["environment"] == "development":
            items = not_in_db[:5]
        else:
            items = not_in_db
        for youtube_id in items:
            get_video_info(youtube_id, WORKING / youtube_id)

            create_video_from_folder(WORKING / youtube_id)


@solara.component
def SectionsControls():
    num_sections = OmegleSection.select().count()
    vids_missing_video = Video.unique_count()
    with solara.Row(justify="center"):
        with solara.Card("Videos"):
            with solara.Column():
                solara.Text(f"Import Videos")
                solara.Button(
                    "Scan Local",
                    on_click=lambda: import_existing_video_files_to_db(
                        STORAGE / "videos"
                    ),
                    classes=["button"],
                )

                solara.Button(
                    f"Download video Files for Unique Videos  {vids_missing_video}",
                    on_click=download_unique,
                    classes=["button"],
                )
                solara.Button(
                    "Check for New Videos",
                    on_click=refresh_from_youtube,
                    classes=["button"],
                )
        with solara.Card("Sections"):
            with solara.Column():
                solara.Text(f"These controls are for creating the")
                solara.Text(f"initial sections for the Omegle Videos")
                solara.Text(f"utilizing the spreadsheet by u/bushman4")
                solara.Warning(f"Should be removed once imported on prod.")
                solara.Button(
                    "Seed Table from CSV", on_click=import_sections, classes=["button"]
                )
                solara.Button(
                    "Create Sections for Videos",
                    on_click=create_omegle_sections,
                    classes=["button"],
                )
    with solara.Row(justify="center"):
        with solara.Card("Channels"):
            solara.Text(f"Import Channels' files")
            solara.Button(
                "Scan Local",
                on_click=lambda: import_channel_files_to_db(STORAGE / "channels"),
                classes=["button"],
            )

        with solara.Card("Subtitle Conversion"):

            num_vtts = (
                SubtitleFileModel.select()
                .where(SubtitleFileModel.path.contains(".en.vtt"))
                .count()
            )

            solara.Text("Creating/Running this on 2025-01-29")
            solara.Error(
                "Delete once run in Prod. Future vtts to be converted before importing"
            )
            solara.Button(
                f"Convert {num_vtts} vtt files to SRT",
                on_click=convert_vtts_to_srts,
                classes=["button"],
            )


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    solara.Markdown(f"# Settings Page")
    SectionsControls()
