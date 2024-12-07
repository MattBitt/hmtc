from time import perf_counter
from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.video_table import VideoTable
from hmtc.domains.video import VideoItem
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Channel,
    Series,
)
from hmtc.models import (
    Section as SectionModel,
)
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import (
    Track as TrackModel,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.models import (
    YoutubeSeries as YoutubeSeriesModel,
)


def create_query_from_url():
    # url options
    # each level should accept 'all' for non-unique videos
    # /videos should be a list of all unique videos (default)
    # /videos/all should include non-unique videos
    # /videos/series/<series_id> should be a list of videos in a series
    # /videos/youtube_series/<youtube_series_id> should be a list of videos in a youtube series
    # /videos/channel/<channel_id> should be a list of videos in a channel
    # /vidoes/album/<album_id> should be a list of videos in an album
    # /videos/playlist/<playlist_id> should be a list of videos in a playlist
    # /videos/sections/none should be a list of videos with no sections
    # /videos/sections/some should be a list of videos with sections
    # /videos/missing-files/audio should be a list of videos missing audio files
    # /videos/missing-files/video should be a list of videos missing video files
    # /videos/missing-files/subtitle should be a list of videos missing subtitle files
    # /videos/missing-files/poster should be a list of videos missing poster files
    # /videos/missing-files/album_nfo should be a list of videos missing album_nfo files
    # /videos/missing-files/info should be a list of videos missing info files
    all = (
        VideoModel.select(
            VideoModel.id,
            VideoModel.unique_content,
            VideoModel.upload_date,
            VideoModel.episode,
            VideoModel.title,
            VideoModel.youtube_id,
            VideoModel.duration,
            VideoModel.jellyfin_id,
            Channel,
            Series,
            YoutubeSeriesModel,
            AlbumModel,
        )
        .join(Channel, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(Series)
        .switch(VideoModel)
        .join(YoutubeSeriesModel, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(AlbumModel, peewee.JOIN.LEFT_OUTER)
    )
    if len(all) == 0:
        return None, None, None, False

    unique = all.where(VideoModel.unique_content == True)

    valid_filters = [
        "series",
        "youtube_series",
        "channel",
        "album",
        "sections",
    ]
    router = solara.use_router()
    # level = solara.use_route_level()
    vids_with_sections = SectionModel.select(SectionModel.video_id).distinct()
    vids_with_sections_ids = [x.video_id for x in vids_with_sections]
    all_vids = VideoModel.select(VideoModel.id).where(VideoModel.unique_content == True)
    vids_without_sections = [
        x.id for x in all_vids if x.id not in vids_with_sections_ids
    ]
    match router.parts:
        case [_, "all"]:
            return all, None, None, True
        case ["videos", "missing-files", file_type]:
            if file_type not in [
                "poster",
                "info",
                "audio",
                "video",
                "subtitle",
                "album_nfo",
            ]:
                logger.error(f"Invalid file type: {file_type}")
                return
            videos_with_files = (
                VideoModel.select(VideoModel)
                .join(FileModel, on=(VideoModel.id == FileModel.video_id))
                .where(FileModel.file_type == file_type)
            )
            all_videos = VideoModel.select(VideoModel).where(
                VideoModel.unique_content == True
            )
            videos = all_videos - videos_with_files
            return videos, "missing-files", file_type, False
        case ["videos", "wednesdays", option]:
            _start = perf_counter()
            if option not in ["have", "need"]:
                logger.error(f"Invalid option: {option}")
                return

            vids = (
                VideoModel.select(VideoModel)
                .join(YoutubeSeriesModel)
                .switch(VideoModel)
                .join(FileModel)
                .where(
                    FileModel.video_id.is_null(False) & (FileModel.file_type == "video")
                )
                .where(YoutubeSeriesModel.title == "Wordplay Wednesday")
            )

            superchat_vid_ids = (
                SuperchatModel.select(SuperchatModel.video_id)
                .where(SuperchatModel.video_id.is_null(False))
                .distinct()
            )

            if option == "have":
                vids = vids.where(VideoModel.id.in_(superchat_vid_ids))

            else:
                vids = vids.where(VideoModel.id.not_in(superchat_vid_ids))

            return vids, "wednesdays", None, False
        case [_, filter, id_to_filter, "all"]:
            if filter in valid_filters:
                return (
                    all.where(getattr(VideoModel, filter) == id_to_filter),
                    filter,
                    id_to_filter,
                    True,
                )
            else:
                logger.debug(f"Invalid filter: {filter}")
                return None, None, None, False
        case [_, filter, id_to_filter]:
            if filter in valid_filters:
                if filter == "sections":
                    if id_to_filter == "none":
                        return (
                            unique.where(VideoModel.id.in_(vids_without_sections)),
                            filter,
                            id_to_filter,
                            False,
                        )
                    elif id_to_filter == "some":
                        return (
                            unique.where(VideoModel.id.in_(vids_with_sections_ids)),
                            filter,
                            id_to_filter,
                            False,
                        )
                    else:
                        logger.debug(f"Invalid section filter: {id_to_filter}")
                        return None, None, None, False
                else:
                    return (
                        unique.where(getattr(VideoModel, filter) == id_to_filter),
                        filter,
                        id_to_filter,
                        False,
                    )
            else:
                logger.debug(f"Invalid filter: {filter}")
                return None, None, None, False
        case [_]:
            query = unique.order_by(VideoModel.upload_date.desc())
            return query, None, None, False
        case _:
            logger.error(f"Invalid URL: {router.parts}")
            raise ValueError("Invalid URL")


def create_table_title(filter, id_to_filter):
    if filter:
        if "channel" in filter:
            table_title = (
                "Channel: " + Channel.get(Channel.id == id_to_filter).name.title()
            )
        elif "youtube_series" in filter:

            table_title = (
                "Youtube Series: "
                + YoutubeSeriesModel.get(
                    YoutubeSeriesModel.id == id_to_filter
                ).title.title()
            )

        elif "series" in filter:
            table_title = (
                "Series: " + Series.get(Series.id == id_to_filter).name.title()
            )
        elif "album" in filter:
            table_title = AlbumModel.get(AlbumModel.id == id_to_filter).title.title()
        else:
            table_title = filter.title()
    else:
        table_title = "All Videos"

    return table_title


def view_details(router, item):
    router.push(f"/video-details/{item['id']}")


def delete_video_item(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_video_item(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]

    episode_number = None

    logger.debug(f"Item received from Vue: {item}")

    video = VideoModel.get(VideoModel.id == item["id"])
    if edited_item["episode"] is not None:
        if (video.episode is None) or (
            int(edited_item["episode"]) != int(video.episode)
        ):
            if not edited_item["episode"].isdigit():
                logger.debug("Episode number is not a digit")
                return

            episode_number = edited_item["episode"]

    new_vid = VideoModel.get_by_id(item["id"])
    new_vid.duration = edited_item["duration"]
    new_vid.jellyfin_id = edited_item["jellyfin_id"]
    new_vid.unique_content = edited_item["unique_content"]
    if episode_number is not None:
        new_vid.episode = episode_number

    new_vid.save()


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)
    base_query, filter, id_to_filter, show_nonunique = create_query_from_url()

    if base_query is None:
        solara.Markdown("No Videos Found")
    else:
        if filter == "wednesdays":
            headers = [
                {"text": "ID", "value": "id", "sortable": True, "align": "right"},
                {"text": "Title", "value": "title", "width": "30%"},
                {"text": "Episode", "value": "episode", "sortable": True},
                {"text": "Superchats", "value": "superchats", "sortable": False},
                {"text": "Segments", "value": "segments_count", "sortable": False},
                {"text": "Actions", "value": "actions", "sortable": False},
            ]
        else:
            headers = [
                {
                    "text": "Upload Date",
                    "value": "upload_date",
                    "sortable": True,
                    "width": "10%",
                },
                {"text": "ID", "value": "id", "sortable": True, "align": "right"},
                {"text": "Title", "value": "title", "width": "30%"},
                {"text": "Duration", "value": "duration", "sortable": True},
                {
                    "text": "Sections",
                    "value": "section_info.section_count",
                    "sortable": False,
                },
                {"text": "Jellyfin ID", "value": "jellyfin_id", "sortable": False},
                {"text": "Files", "value": "file_count", "sortable": False},
                {"text": "Actions", "value": "actions", "sortable": False},
            ]

        search_fields = [VideoModel.youtube_id, VideoModel.title]
        VideoTable(
            router=router,
            headers=headers,
            base_query=base_query,
            search_fields=search_fields,
        )
