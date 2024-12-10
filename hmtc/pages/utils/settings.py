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
from hmtc.domains.album import Album as AlbumItem
from hmtc.domains.track import Track as TrackItem
from hmtc.domains.video import Video as VideoItem
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import Channel
from hmtc.models import Section as SectionModel
from hmtc.models import (
    SectionTopic as SectionTopicsModel,
)
from hmtc.models import Superchat as SuperchatModel
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
from hmtc.utils.importer.seed_database import recreate_database
from hmtc.utils.jellyfin_functions import search_for_media
from hmtc.utils.opencv.image_extractor import ImageExtractor

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


@solara.component_vue("../../components/GOBY/ButtonShowcase.vue")
def ButtonShowCase():
    pass


def remake_db():
    db = VideoModel._meta.database
    recreate_database(db)


class PageState:
    updating = solara.reactive(False)
    i = solara.reactive(0)
    num_to_download = solara.reactive(10)
    bad_superchat_path_videos = solara.reactive([])

    @staticmethod
    def rip_ww_screenshots():
        logger.debug("Ripping Wordplay Wednesday Screenshots")
        _output_path = STORAGE / "ww_screenshots"
        if not _output_path.exists():
            _output_path.mkdir(parents=True, exist_ok=True)
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
            .limit(20)
        )
        logger.debug(f"Found {len(vids)} Wordplay Wednesday videos")
        for v in vids:
            video_file = None
            video = VideoItem.from_model(v)
            for f in video.files:
                if f.file_type == "video":
                    video_file = Path(f.path) / f.filename
                    break
            if video_file is None:
                raise Exception(f"No video file found for {video.title}")

            this_output_path = _output_path / f"ww{str(video.episode).zfill(3)}"
            if not this_output_path.exists():
                this_output_path.mkdir(parents=True, exist_ok=True)
            extractor = ImageExtractor(
                input_video_path=video_file, output_path=this_output_path
            )
            if extractor is None:
                logger.error(f"No video file found for {video.title}")
                continue
            extractor.save_n_random_frames(10)
            logger.success(f"Saved 10 random frames for {video.title}")

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
    def find_bad_superchat_paths():
        logger.error(f"Checking for bad superchat paths")
        bad_videos = set()
        superchat_files = (
            SuperchatFileModel.select(SuperchatFileModel.superchat_id)
            .where(
                (SuperchatFileModel.file_type == "image")
                & (SuperchatFileModel.path.contains("videos/None"))
            )
            .distinct()
        )
        for scf in superchat_files:
            superchat = SuperchatModel.get_by_id(scf.superchat_id)
            video = VideoModel.get_by_id(superchat.video.id)
            bad_videos.add(video.title)
        logger.error(f"Found {len(bad_videos)} bad superchat paths")
        for vid in bad_videos:
            logger.error(f"Bad video: {vid}")
            # file.delete_instance()
        PageState.bad_superchat_path_videos.set(list(bad_videos)[0:50])
        logger.error(f"Finished Checking for bad superchat paths")


status = solara.reactive("")


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
                classes=["button"],
            )

        with solara.Card("Troublshooting functions"):
            solara.Button(
                label="Find bad superchat Paths",
                classes=["button"],
                on_click=PageState.find_bad_superchat_paths,
            )
        with solara.Card("Bad Superchat Videos"):
            solara.Text(
                str(len(PageState.bad_superchat_path_videos.value)),
                classes=["mywarning"],
            )
            for v in PageState.bad_superchat_path_videos.value:
                with solara.Row():
                    solara.Text(v)
        if config["general"]["environment"] != "production":
            solara.Button("Recreate Database", on_click=remake_db)
