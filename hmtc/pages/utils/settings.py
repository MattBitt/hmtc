from pathlib import Path

import peewee
import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.config import init_config
from hmtc.domains.album import Album
from hmtc.domains.channel import Channel
from hmtc.domains.disc import Disc
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Album as AlbumModel
from hmtc.models import Channel as ChannelModel
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import ImageFile, OmegleSection, Thumbnail, VideoFiles
from hmtc.models import Section as SectionModel
from hmtc.models import SubtitleFile as SubtitleFileModel
from hmtc.models import Topic as TopicModel
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
            items = not_in_db[:1]
        else:
            items = not_in_db
        for youtube_id in items:
            get_video_info(youtube_id, WORKING / youtube_id)

            create_video_from_folder(WORKING / youtube_id)


def create_short_sections():
    vids_with_sections = SectionModel.select(SectionModel.video_id).distinct()
    short_vids_with_no_sections = VideoModel.select().where(
        (
            VideoModel.id.not_in(vids_with_sections)
            & (VideoModel.duration < 600)
            & (VideoModel.unique_content == True)
        )
    )

    for vid in short_vids_with_no_sections:
        video = Video(vid)
        video.create_single_section()

    logger.success(f"Finished creating {len(short_vids_with_no_sections)} sections.")


def create_album_folders():
    albums = AlbumModel.select()
    for alb in albums:
        a = Album(alb.id)
        a.create_folders()


def zero_pad_disc_title(orig_title):
    padded = orig_title[5:]
    return "Disc " + padded.zfill(3)


def create_disc_folders():
    discs = DiscModel.select()

    for disc in discs:
        if disc.folder_name is None or len(disc.folder_name) < 8:
            disc.folder_name = zero_pad_disc_title(disc.title)
            disc.save()
        d = Disc(disc.id)
        d.create_folders()


def delete_nonunique_sections():
    non_unique_vids = VideoModel.select().where(VideoModel.unique_content == False)
    sects = SectionModel.select().where(SectionModel.video_id.in_(non_unique_vids))

    logger.debug(f"{len(sects)}")
    for sect in sects:
        logger.debug(f"Deleting sections from {sect.video.title}")
        sect.delete_instance()


@solara.component
def Folders():
    with solara.Card("Album Folders"):
        with solara.Column():
            solara.Button(
                "Create Album Folders",
                on_click=create_album_folders,
                icon_name=Icons.ALBUM.value,
                classes=["button"],
            )
            solara.Button(
                "Create Disc Folders",
                on_click=create_disc_folders,
                icon_name=Icons.DISC.value,
                classes=["button"],
            )


@solara.component
def SectionsControls():
    with solara.Columns([6, 6]):
        with solara.Card("Videos"):
            with solara.Column():
                solara.Button(
                    "Check for New Videos",
                    on_click=refresh_from_youtube,
                    icon_name=Icons.DOWNLOAD.value,
                    classes=["button"],
                )
                solara.Button(
                    "Delete Non-Unique Sections",
                    on_click=delete_nonunique_sections,
                    icon_name=Icons.SECTION.value,
                    classes=["button"],
                )
        with solara.Card("Pipelines"):
            with solara.Columns():
                with solara.Link(f"/api/videos/pipeline/sectionalize"):
                    solara.Button(
                        "Sectionalize",
                        icon_name=Icons.SECTION.value,
                        classes=["button"],
                    )
                with solara.Link(f"/api/videos/pipeline/finetune"):
                    solara.Button(
                        "Fine Tune",
                        icon_name=Icons.FINETUNER.value,
                        classes=["button"],
                    )


@solara.component
def Page():
    router = solara.use_router()
    SectionsControls()
    Folders()
