import csv
import operator
import os
from itertools import groupby
from pathlib import Path

import peewee
import solara
from loguru import logger

from hmtc.components.shared.progress_slider import SimpleProgressBar
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import Channel
from hmtc.models import (
    File as FileModel,
)

from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopics as SectionTopicsModel,
)
from hmtc.models import (
    Topic as TopicModel,
)
from hmtc.models import Track as TrackModel
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)
from hmtc.schemas.album import Album as AlbumItem
from hmtc.schemas.file import File as FileItem
from hmtc.schemas.file import FileManager
from hmtc.schemas.section import Section, SectionManager
from hmtc.schemas.track import Track as TrackItem
from hmtc.schemas.video import VideoItem
from hmtc.utils.jellyfin_functions import search_for_media

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


def create_album_xmls():
    # added on 9/25/24
    # run in production on ??????
    vids_with_album_xml = (
        VideoModel.select(VideoModel.id)
        .join(FileModel)
        .where(FileModel.file_type == "album_nfo")
        .distinct()
    )
    vids = (
        VideoModel.select(VideoModel.id, FileModel.file_type)
        .join(FileModel)
        .where(
            (VideoModel.id.not_in(list(vids_with_album_xml)))
            & ((FileModel.file_type == "video") | (FileModel.file_type == "audio"))
        )
    )
    logger.error(f"Creating Album XMLs for {len(vids)} videos")
    for v in vids:
        album_nfo_path = VideoItem.create_xml_for_jellyfin(v.id)
        # logger.debug(f"Created album.nfo for {v.title} at {album_nfo_path}")
        # file = FileItem.from_path(album_nfo_path)
        # file_path = Path(file.path) / file.filename
        album_nfo = FileManager.add_path_to_video(album_nfo_path, v)
        logger.debug(f"Created album.nfo file for {v.title} at {album_nfo}")


class PageState:
    updating = solara.reactive(False)
    i = solara.reactive(0)
    num_to_download = solara.reactive(10)

    @staticmethod
    def rip_ww_screenshots():
        logger.debug("Ripping Wordplay Wednesday Screenshots")
        PageState.updating.set(True)
        vids = (
            VideoModel.select()
            .join(
                YoutubeSeriesModel,
                on=(VideoModel.youtube_series_id == YoutubeSeriesModel.id),
            )
            .switch(VideoModel)
            .join(FileModel, on=(VideoModel.id == FileModel.video_id))
            .where(
                (FileModel.file_type == "video")
                & (YoutubeSeriesModel.title == "Wordplay Wednesday")
            )
        )
        logger.debug(f"Found {len(vids)} Wordplay Wednesday videos")
        # this seems to work. good starting point for ripping screenshots

    @staticmethod
    def create_tracks_from_sections():
        # this is another temporary function to auto create tracks
        # from the original sections
        logger.error("About to create tracks from sections")
        sections = SectionModel.select(
            SectionModel.id, SectionModel.video_id, SectionModel.start, SectionModel.end
        ).where(SectionModel.track_id.is_null())
        logger.error(f"Found {len(sections)} sections with no track")
        for sec in sections:
            video = (
                VideoModel.select(VideoModel, FileModel)
                .join(FileModel)
                .where(
                    (VideoModel.id == sec.video_id) & (FileModel.file_type == "audio")
                )
                .get_or_none()
            )
            if video is None:
                logger.error(f"No audio file found for {sec.video_id}")
                continue
            if video.album is not None:
                album = AlbumModel.get_by_id(video.album.id)
                album_item = AlbumItem.from_model(album)
                track_item = album_item.create_from_section(section=sec, video=video)
                # abc = [Path(z.path) / z.filename for z in video.files]
                # if len(abc) > 0:
                if video.file:
                    input_file = Path(video.file.path) / video.file.filename
                    output_file = track_item.write_file(input_file=input_file)
                    FileManager.add_path_to_track(output_file, track_item, video)
                    logger.error(f"Created track {track_item.title} for {video.title}")
                else:
                    logger.error(
                        f"In write_file loop. No audio file found for {video.title}"
                    )
            else:
                logger.error(f"No album found for {video.title}")

    @staticmethod
    def search_for_jellyfin_ids():
        vids = VideoModel.select(VideoModel).where(
            (
                VideoModel.jellyfin_id.is_null() & VideoModel.contains_unique_content
                == True
            )
        )

        logger.debug(f"Found {len(vids)} videos with no jellyfin id and unique content")
        for v in vids:
            if v.youtube_id is None:
                logger.error(f"No youtube id found for {v.title}")
                continue

            existing = PageState.jf.search_media(v.youtube_id)
            if existing is None:
                logger.error(f"{v.youtube_id} not found in Jellyfin")
                continue
            if existing["TotalRecordCount"] == 1:
                v.jellyfin_id = existing["Items"][0]["Id"]
                v.save()
                logger.debug(f"Assigned {v.jellyfin_id} to {v.title}")
            elif existing["TotalRecordCount"] > 1:
                for item in existing["Items"]:
                    if item["Type"] == "Audio":
                        v.jellyfin_id = item["Id"]
                        v.save()
                        logger.debug(f"Assigned {v.jellyfin_id} to {v.title}")
                        break
            else:
                logger.error(f"No results found for {v.youtube_id}")

    @staticmethod
    def search_for_video_jellyfin_ids():
        videos = (
            VideoModel.select(VideoModel, FileModel)
            .join(
                FileModel,
                peewee.JOIN.LEFT_OUTER,
                on=VideoModel.id == FileModel.video_id,
            )
            .where(VideoModel.jellyfin_id.is_null())
        )
        found_videos = 0
        logger.debug(f"Found {len(videos)} videos with no jellyfin id")
        for v in videos:
            existing_item = search_for_media(library="videos", title=str(v.youtube_id))
            if existing_item is None:
                continue
            found_videos += 1
            v.jellyfin_id = existing_item["Id"]
            v.save()
        logger.error(f"Found jellyfin ids for {found_videos} videos")

    @staticmethod
    def search_for_track_jellyfin_ids():
        tracks = (
            TrackModel.select(TrackModel, FileModel)
            .join(
                FileModel,
                peewee.JOIN.LEFT_OUTER,
                on=TrackModel.id == FileModel.track_id,
            )
            .where(TrackModel.jellyfin_id.is_null())
        )

        logger.debug(f"Found {len(tracks)} tracks with no jellyfin id")
        for t in tracks:
            existing_item = search_for_media(library="tracks", title=str(t.title))
            if existing_item is None:
                continue
            t.jellyfin_id = existing_item["Id"]
            t.save()

    @staticmethod
    def create_lyrics_files_for_existing_tracks():
        tracks_with_lyrics = (
            TrackModel.select(TrackModel.id)
            .join(
                FileModel,
                peewee.JOIN.LEFT_OUTER,
                on=TrackModel.id == FileModel.track_id,
            )
            .where(FileModel.file_type == "lyrics")
        ).distinct()
        total_tracks = TrackModel.select(TrackModel.id)

        tracks = total_tracks.where(TrackModel.id.not_in(tracks_with_lyrics))
        logger.error(f"Found {len(total_tracks)} tracks in total")
        logger.error(f"Found {len(tracks_with_lyrics)} tracks with lyrics file")
        logger.error(f"Found {len(tracks)} tracks with no lyrics file")
        for track in tracks:
            section = track.section.get_or_none()
            if section is None:
                logger.error(f"No video found for {track}")
                continue
            video_id = section.video.id

            video = VideoModel.get_by_id(video_id)
            try:
                input_file = (
                    FileModel.select()
                    .where(
                        (FileModel.video_id == video_id)
                        & (FileModel.file_type == "subtitle")
                    )
                    .get()
                )
            except:
                logger.error(f"No input file found for")
                continue
            input_file_path = Path(input_file.path) / input_file.filename
            track_item = TrackItem.from_model(TrackModel.get_by_id(track.id))
            lyrics_path = track_item.write_lyrics_file(input_file=input_file_path)

            new_file = FileManager.add_path_to_track(
                path=lyrics_path, track=track_item, video=video
            )
            logger.debug(f"Created lyrics file {new_file}")

    @staticmethod
    def download_empty_video_info():
        logger.debug("Downloading empty video info")
        PageState.updating.set(True)
        vids = (
            VideoModel.select()
            .where(VideoModel.duration.is_null())
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
    def sync_channels_from_youtube():
        logger.debug("Syncing channel_id in Database from youtube")
        PageState.updating.set(True)
        vids_with_no_channel = VideoItem.get_vids_with_no_channel()
        if len(vids_with_no_channel) == 0:
            logger.debug("All videos have a channel assigned.")
            status.set("All videos have a channel assigned.")
            return
        else:
            logger.debug(f"Found {len(vids_with_no_channel)} videos with no channel")
            status.set(f"Found {len(vids_with_no_channel)} videos with no channel")

        channels = Channel.select().where(
            (Channel.enabled == True) & (Channel.name.contains("Harry"))
        )

        for c in channels:
            status.set(f"Checking Channel {c.name}")

            yt_ids = c.grab_ids()
            for vid in vids_with_no_channel:
                if vid.youtube_id in yt_ids:
                    vid.channel_id = c.id
                    vid.save()
                    logger.debug(f"Assigned {vid} to {c}")
                    PageState.i.set(PageState.i.value + 1)

            status.set("Finished synching channel ids to videos in database")

        PageState.updating.set(False)

    # this is a temporary function to update the episode numbers for videos
    # as of 8-16-2024
    @staticmethod
    def update_episode_numbers():
        logger.debug("Updating episode numbers")
        PageState.updating.set(True)
        vids = VideoItem.get_vids_with_no_episode_number()
        logger.debug(f"Found {len(vids)} videos with no episode number")
        for v in vids:
            v.update_episode_number()
            PageState.i.set(PageState.i.value + 1)
        PageState.updating.set(False)

    # this is a temporary function to create albums for videos that are part of a youtube series
    # still working on this on 10/14/24
    # need to remove it after ive run it in production
    def create_yts_albums():
        logger.debug("Creating Albums for YT Series")
        vids = (
            VideoModel.select(
                VideoModel.id,
                VideoModel.youtube_series,
                VideoModel.episode,
                VideoModel.upload_date,
            )
            .join(YoutubeYoutubeSeriesModel)
            .where(
                (
                    (VideoModel.contains_unique_content == True)
                    & (VideoModel.album_id.is_null())
                    & (VideoModel.youtube_series.is_null(False))
                    & (VideoModel.episode.is_null(False))
                )
            )
            .order_by(VideoModel.upload_date)
        )
        logger.error(f"Found {len(vids)} videos to create an album for")
        for v in vids:
            if v.episode[-1].isalpha():
                ep_no = v.episode[:-1]
            else:
                ep_no = v.episode
            title = v.youtube_series.title + " " + str(ep_no).zfill(3)
            album_info = dict(
                title=title,
                release_date=v.upload_date,
            )
            existing = (
                AlbumModel.select(AlbumModel.id)
                .where(AlbumModel.title == title)
                .get_or_none()
            )
            if existing:
                album = existing
            else:
                album = AlbumModel.create(**album_info)

            vid = VideoModel.get_by_id(v.id)

            vid.album = album
            vid.save()
            logger.debug(f"Created Album {album} for {v}")
        logger.error(
            "Finished creating albums Videos with no album, a YT series, and an episode number"
        )

    # this is a temporary function to assign video posters to albums
    # 10/21/24
    def assign_video_posters_to_albums():
        albums_with_posters = FileModel.select(FileModel.album_id).where(
            (FileModel.file_type == "poster") & (FileModel.album_id.is_null(False))
        )
        logger.error(f"Found {albums_with_posters.count()} albums WITH a poster")
        all_albums = AlbumModel.select(AlbumModel.id)
        albums_missing_posters = all_albums.where(
            AlbumModel.id.not_in(albums_with_posters)
        )
        logger.error(f"Found {albums_missing_posters.count()} albums with no poster")
        for album_id in albums_missing_posters:
            try:
                album = AlbumModel.get_by_id(album_id)
            except Exception as e:
                logger.error(f"{e}: Album with id {album_id} not found")
                continue
            try:
                vid = album.videos[0]
            except Exception as e:
                logger.error(f"{e}: No video found for album {album}")
                continue

            vid_poster = (
                FileModel.select()
                .where(
                    (FileModel.file_type == "poster") & (FileModel.video_id == vid.id)
                )
                .get_or_none()
            )
            if vid_poster:
                album_item = AlbumItem.from_model(album)
                album_item.use_video_poster()
            else:
                logger.info(f"No poster found for {vid.title}. Skipping")

    @staticmethod
    def import_track_info():
        grouped_tracks = import_tracks()
        for id, tracks in grouped_tracks:
            video = VideoItem.get_by_youtube_id(id)
            if video:
                # album = Album.grab_for_video(video.id)
                # if not album:
                #     album = Album.create_for_video(video)
                # if video.duration == 0 or video.duration is None:
                #     video.duration = 7200

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
                    topics = track["title"].split(",")
                    for t in topics:
                        new_topic, _ = TopicModel.get_or_create(text=t.strip().lower())
                        num_topics_in_section = (
                            SectionTopicsModel.select()
                            .where(SectionTopicsModel.section_id == section)
                            .count()
                        )
                        SectionTopicsModel.create(
                            topic_id=new_topic.id,
                            section=section,
                            order=num_topics_in_section + 1,
                        )
                logger.debug(f"Section created: {section}")

    @staticmethod
    def update_episode_numbers_omegle_exlusive():
        logger.debug("Updating episode numbers")
        PageState.updating.set(True)
        vids = VideoItem.get_vids_with_no_episode_number()
        ex_omegle = [v for v in vids if "omegle" in v.title.lower()]
        episode_number = 0
        for v in sorted(ex_omegle, key=lambda x: x.upload_date):
            episode_number += 1
            v.set_episode_number(episode_number)
            # v.update_episode_number()
            PageState.i.set(PageState.i.value + 1)
        PageState.updating.set(False)

    @staticmethod
    def update_episode_numbers_guerilla_exlusive():
        logger.debug("Updating episode numbers")
        PageState.updating.set(True)
        vids = VideoItem.get_vids_with_no_episode_number()
        ex_gb = [v for v in vids if "guerilla" in v.title.lower()]
        episode_number = 0
        for v in sorted(ex_gb, key=lambda x: x.upload_date):
            # v.update_episode_number()
            episode_number += 1
            v.set_episode_number(episode_number)
            PageState.i.set(PageState.i.value + 1)
        PageState.updating.set(False)


@solara.component
def OldControls():
    with solara.Card("Use at your own peril"):
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

        solara.Button(
            label="Import Track Info",
            on_click=PageState.import_track_info,
            classes=["button"],
        )

        solara.Button(
            label="Create Tracks from Sections",
            on_click=PageState.create_tracks_from_sections,
            classes=["button"],
        )


status = solara.reactive("")


@solara.component_vue("../components/GOBY/ButtonShowcase.vue")
def ButtonShowCase():
    pass


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )
    ButtonShowCase()
    with solara.Column(classes=["main-container"]):
        with solara.Card("Reusuable Functions"):
            solara.Button(
                label="Assign jellyfin ids to videos (10/30/24)",
                on_click=PageState.search_for_video_jellyfin_ids,
                classes=["button"],
            )
            solara.Button(
                label="Assign jellyfin ids to tracks (10/28/24)",
                on_click=PageState.search_for_track_jellyfin_ids,
                classes=["button"],
            )
            solara.Button(
                label="Rip Wordplay Wednesday screen shots 11/16/24",
                on_click=PageState.rip_ww_screenshots,
            )
