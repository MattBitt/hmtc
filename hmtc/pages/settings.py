import csv
import solara
import operator
from itertools import groupby

from loguru import logger
from pathlib import Path
import os
from hmtc.components.shared.progress_slider import SimpleProgressBar
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Channel
from hmtc.models import Video as VideoTable
from hmtc.schemas.video import VideoItem
from hmtc.mods.album import Album, Track
from hmtc.mods.section import SectionManager, Section
from hmtc.config import init_config
from hmtc.mods.track import TrackItem

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH")) / "media_info"
config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])


def import_tracks():
    track_file = MEDIA_INFO / "tracks/track_info.csv"
    with open(track_file, "r", encoding="utf") as f:
        csv_file = csv.DictReader(f)
        tracks = []
        for row in csv_file:
            tracks.append(
                dict(
                    title=row["words"],
                    youtube_id=row["youtube_id"],
                    start=row["start"],
                    end=row["end"],
                    length=row["length"],
                )
            )
            pass
    key_func = operator.itemgetter("youtube_id")
    return groupby(tracks, key=key_func)


class PageState:
    updating = solara.reactive(False)
    i = solara.reactive(0)
    num_to_download = solara.reactive(10)

    @staticmethod
    def download_empty_video_info():
        logger.debug("Downloading empty video info")
        PageState.updating.set(True)
        vids = (
            VideoTable.select()
            .where(VideoTable.duration.is_null())
            .limit(PageState.num_to_download.value)
        )
        logger.info(f"Updating {len(vids)} videos")
        for v in vids:
            vt = VideoItem.from_orm(v)
            try:
                vt.update_from_youtube()
            except Exception as e:
                logger.error(f"Error updating video: {e}")

            PageState.i.set(PageState.i.value + 1)
        logger.info("finished updating videos")
        PageState.i.set(0)
        PageState.updating.set(False)

    @staticmethod
    def download_missing_media_files():
        logger.debug("Downloading missing media files")
        PageState.updating.set(True)
        vids = VideoItem.get_vids_with_no_media_files(
            limit=PageState.num_to_download.value
        )
        logger.info(f"Updating {len(vids)} videos")
        for v in vids:
            try:
                v.download_video()
            except Exception as e:
                logger.error(f"Error updating video: {e}")

            PageState.i.set(PageState.i.value + 1)
        logger.info("finished updating videos")
        PageState.i.set(0)
        PageState.updating.set(False)

    @staticmethod
    def refresh_videos_from_youtube():
        logger.debug(f"Refreshing videos from youtube")
        PageState.updating.set(True)
        existing_ids = [v.youtube_id for v in VideoItem.get_youtube_ids()]

        channels = Channel.select().where(Channel.enabled == True)
        for c in channels:
            yt_ids = c.grab_ids()

            for id in yt_ids:
                if id not in existing_ids:
                    logger.debug(f"Found a new video. Adding to Database {id}")

                    VideoItem.create_from_youtube_id(id)
                    PageState.i.set(PageState.i.value + 1)
        PageState.updating.set(False)

    @staticmethod
    def import_track_info():
        grouped_tracks = import_tracks()
        current_id = None
        for id, tracks in grouped_tracks:

            video = VideoItem.get_by_youtube_id(id)
            if video:
                album = Album.grab_for_video(video.id)
                if not album:
                    album = Album.create_for_video(video)
                if video.duration == 0 or video.duration is None:
                    video.duration = 7200

                sm = SectionManager.from_video(video)
                if len(sm.sections) > 0:
                    logger.error(f"Sections already exist for {video}. Skipping Import")
                    continue

                for track in tracks:
                    section = sm.create_section(
                        start=int(track["start"]),
                        end=int(track["end"]),
                        section_type="instrumental",
                    )
                logger.debug(f"Section created: {section}")

    @staticmethod
    def create_tracks_from_sections():

        for sect in Section.get_all():
            vid = VideoItem.get_by_id(sect.video_id)
            album = VideoItem.get_album(video_id=vid.id)
            track = TrackItem.create_from_section(video=vid, album=album, section=sect)
            if track:
                track.write_file()
        pass


@solara.component
def Page():
    router = solara.use_router()

    MySidebar(
        router=router,
    )

    with solara.Column(classes=["main-container"]):
        with solara.Column():
            if PageState.updating.value:
                with solara.Card():
                    solara.Text("Updating Videos")
                    SimpleProgressBar(
                        label="Videos Updated",
                        current_value=PageState.i.value,
                        total=PageState.num_to_download.value,
                        color="blue",
                    )
            else:
                with solara.Card():
                    solara.InputInt(
                        label="Number of Videos to Download",
                        value=PageState.num_to_download,
                    )
                    solara.Button(
                        label="Download info for Random Videos!",
                        on_click=PageState.download_empty_video_info,
                        classes=["button"],
                    )
                    solara.Button(
                        label="Download media files for Random Videos! (be careful with big numbers....)",
                        on_click=PageState.download_missing_media_files,
                        classes=["button"],
                    )
                with solara.Card():
                    solara.Button(
                        label="Check for New Videos",
                        on_click=PageState.refresh_videos_from_youtube,
                        classes=["button"],
                    )
                with solara.Card():
                    solara.Button(
                        label="Import Track Info",
                        on_click=PageState.import_track_info,
                        classes=["button"],
                    )
                with solara.Card():
                    solara.Button(
                        label="Create Tracks from Sections",
                        on_click=PageState.create_tracks_from_sections,
                        classes=["button"],
                    )
