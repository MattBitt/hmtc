import os
import shutil
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
from hmtc.models import DiscFiles as DiscFilesModel
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import ImageFile, OmegleSection, Thumbnail, VideoFiles
from hmtc.models import Section as SectionModel
from hmtc.models import SubtitleFile as SubtitleFileModel
from hmtc.models import Topic as TopicModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.utils.importer.existing_files import (
    create_omegle_sections,
    create_video_from_folder,
    import_channel_files_to_db,
    import_existing_video_files_to_db,
    import_sections,
)
from hmtc.utils.mutagen_utils import write_id3_tags, write_mp4_metadata
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


def create_album_folders():
    albums = AlbumModel.select()
    for alb in albums:
        a = Album(alb.id)
        a.create_folders()


def create_disc_posters():
    discs_with_posters = DiscFilesModel.select().where(
        DiscFilesModel.poster_id.is_null(False)
    )
    discs_without = DiscModel.select().where(DiscModel.id.not_in(discs_with_posters))
    logger.debug(f"Found {len(discs_without)} missing posters")
    for disc in discs_without:
        _disc = Disc(disc)
        vid = _disc.videos()[0]
        video = Video(vid)
        _disc.use_poster_from_video(video)
        logger.debug(f"{video}")


def zero_pad_disc_title(orig_title):
    padded = orig_title[5:]
    return "Disc " + padded.zfill(3)


def title_from_order(order):
    return "Disc " + str(order).zfill(3)


def fix_album_discs():
    # fixes gaps in contiguous discs
    albums = AlbumModel.select()
    for album in albums:
        # this is a list so it doesn't alter the query when updating the order
        # may not be needed...
        discs = list(
            DiscModel.select()
            .where(DiscModel.album_id == album.id)
            .order_by(DiscModel.order.asc())
        )
        logger.debug(f"{album} has {len(discs)} discs currently. Checking for gaps")
        if len(discs) == 0:
            logger.debug(f"No discs found for {album}. Skipping")
            continue
        start = discs[0].order
        if start > 1:
            logger.error(f"Error")
            continue

        for index, disc in enumerate(discs, start):
            if disc.order != index:
                logger.debug(f"Found non-match {index=} {disc.order=}")
                disc.order = index
                disc.title = title_from_order(index)
                disc.folder_name = title_from_order(index)
                disc.save()


def reorder_exclusives():
    albums = AlbumModel.select().where(
        (AlbumModel.title == "Omegle Bars") | (AlbumModel.title == "Guerrilla Bars")
    )
    for album in albums:
        exclusive_disc = (
            DiscModel.select()
            .where((DiscModel.album_id == album.id) & (DiscModel.order == 0))
            .get_or_none()
        )
        if exclusive_disc is None:
            logger.error(f"No 'exclusive disc' found for {album}")
            continue
        dvs = DiscVideoModel.select().where(DiscVideoModel.disc_id == exclusive_disc.id)
        num_videos = len(dvs)

        for dv in dvs:
            dv.order = dv.order + 1000
            dv.save()
        vids_on_disk = [dv.video.id for dv in dvs]
        vids_in_order = (
            VideoModel.select()
            .where(VideoModel.id.in_(vids_on_disk))
            .order_by(VideoModel.upload_date.asc())
        )
        for i, vid in enumerate(vids_in_order, 1):
            _dv = (
                DiscVideoModel.select()
                .where(
                    (DiscVideoModel.disc_id == exclusive_disc.id)
                    & (DiscVideoModel.video_id == vid.id)
                )
                .get_or_none()
            )
            if _dv is None:
                logger.error(f"_dv is None...")
                continue
            _dv.order = i
            _dv.save()
        logger.debug(f"About to reorder {exclusive_disc} on album {album}")


def delete_empty_folders():
    library_folder = STORAGE / "libraries"
    for item in library_folder.glob("**/*"):
        if item.is_file():
            continue
        if len(os.listdir(item)) == 0:
            shutil.rmtree(item)


def create_tracks_from_ft_sections():
    sections_with_tracks = TrackModel.select(TrackModel.section_id).distinct()
    sections = SectionModel.select().where(
        (SectionModel.fine_tuned == True)
        & (SectionModel.id.not_in(sections_with_tracks))
    )
    for section in sections:
        dv = section.video.dv.get_or_none()
        if dv is None:
            logger.debug(f"No disc (Album) assigned....")
            return
        disc = Disc(dv.disc_id)
        disc.create_tracks()


def fix_id3_release_date():
    from hmtc.domains.track import Track

    # this was used to fix the initial tracks created with
    # the video upload date as the id3 tag. this made jf
    # saw the albums as sepearate.
    tracks = TrackModel.select()
    for _track in tracks:
        track = Track(_track)

        new_tag = dict(date=str(track.instance.disc.album.release_date)[0:4])
        mp3_file = track.get_file("audio")
        if mp3_file is not None:
            write_id3_tags(mp3_file, new_tag)


def update_album_release_dates():
    from hmtc.domains.album import Album

    albums = AlbumModel.select()
    for _album in albums:
        album = Album(_album)
        first_vid = (
            album.discs_and_videos()
            .order_by(VideoModel.upload_date.asc())
            .get_or_none()
        )

        if first_vid is not None:
            album.instance.release_date = first_vid.upload_date
            album.instance.save()


@solara.component
def Folders():
    with solara.Card("Album"):
        with solara.Column():
            solara.Button(
                "Create Disc Posters",
                on_click=create_disc_posters,
                icon_name=Icons.DISC.value,
                classes=["button"],
                disabled=True,  # ran in prod on 3/1/25
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
                    "Create Tracks From FT Sections",
                    on_click=create_tracks_from_ft_sections,
                    icon_name=Icons.TRACK.value,
                    classes=["button"],
                )
        with solara.Card("Pipelines"):
            with solara.Column():
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
                with solara.Link(f"/api/videos/pipeline/sections"):
                    solara.Button(
                        "Sections",
                        icon_name=Icons.SECTION.value,
                        classes=["button"],
                        disabled=True,  # ran on 2/28/25
                    )


@solara.component
def AlbumCard():

    with solara.Card("Quick Fixes"):
        with solara.Column():
            solara.Button(
                "Delete Empty Folders in Libraries",
                on_click=delete_empty_folders,
                icon_name=Icons.DELETE.value,
                classes=["button mywarning"],
                disabled=False,
            )
            solara.Button(
                "Fix release date on ID3 tags",
                on_click=fix_id3_release_date,
                icon_name=Icons.AUDIO.value,
                classes=["button"],
                disabled=True,  # ran in prod on 3/1/25
            )


@solara.component
def Page():
    router = solara.use_router()
    SectionsControls()
    with solara.Columns([6, 6]):
        Folders()
        AlbumCard()
