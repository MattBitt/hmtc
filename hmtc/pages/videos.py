from typing import Callable

import pandas as pd
import peewee
import solara
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import (
    Album as AlbumModel,
)
from hmtc.models import (
    Channel,
    Playlist,
    Series,
    YoutubeSeries,
)
from hmtc.models import (
    Video as VideoModel,
)
from hmtc.schemas.video import VideoItem


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

    all = (
        VideoModel.select(
            VideoModel.id,
            VideoModel.contains_unique_content,
            VideoModel.upload_date,
            VideoModel.episode,
            VideoModel.title,
            VideoModel.youtube_id,
            VideoModel.duration,
            VideoModel.jellyfin_id,
            Channel,
            Series,
            Playlist,
            YoutubeSeries,
            AlbumModel,
        )
        .join(Channel, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(Series)
        .switch(VideoModel)
        .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(Playlist, peewee.JOIN.LEFT_OUTER)
        .switch(VideoModel)
        .join(AlbumModel, peewee.JOIN.LEFT_OUTER)
    )

    unique = all.where(VideoModel.contains_unique_content == True)

    valid_filters = ["series", "youtube_series", "channel", "album", "playlist"]
    router = solara.use_router()
    # level = solara.use_route_level()

    match router.parts:
        case [_, "all"]:
            # should probably show the unique column if all are shown
            return all, None, None, True
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
            # this is the /videos page view
            return unique, None, None, False
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
                + YoutubeSeries.get(YoutubeSeries.id == id_to_filter).title.title()
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
    selected_channel = dict_of_items["selectedChannel"]
    selected_series = dict_of_items["selectedSeries"]
    selected_youtube_series = dict_of_items["selectedYoutubeSeries"]
    selected_album = dict_of_items["selectedAlbum"]

    channel = None
    playlist = None
    youtube_series = None
    album = None
    episode_number = None

    # 10/5/24 this is a hack to allow me to delete series from videos
    new_series = "asdf"

    logger.debug(f"Item received from Vue: {item}")
    video_item = VideoItem.get_by_id(item["id"])

    if selected_channel["id"] is not None:
        if video_item.channel is None or (
            selected_channel["id"] != video_item.channel.id
        ):
            channel = Channel.get_by_id(selected_channel["id"])

    if selected_series is None:
        new_series = None
    elif selected_series["id"] is not None:
        if video_item.series is None or (selected_series["id"] != video_item.series.id):
            new_series = Series.get_by_id(selected_series["id"])

    if selected_youtube_series["id"] is not None:
        if video_item.youtube_series is None or (
            selected_youtube_series["id"] != video_item.youtube_series.id
        ):
            youtube_series = YoutubeSeries.get_by_id(selected_youtube_series["id"])

    # starting to deprecate (youtube) playlists 9/27/24
    # if selected_playlist["id"] is not None:
    #     if video_item.playlist is None or (
    #         selected_playlist["id"] != video_item.playlist.id
    #     ):
    #         playlist = Playlist.get_by_id(selected_playlist["id"])

    if selected_album["id"] is not None:
        if (video_item.album is None) or (selected_album["id"] != video_item.album.id):
            album = AlbumModel.get_by_id(selected_album["id"])

    if edited_item["episode"] is not None:
        if (video_item.episode is None) or (
            int(edited_item["episode"]) != int(video_item.episode)
        ):
            if not edited_item["episode"].isdigit():
                logger.debug("Episode number is not a digit")
                return

            episode_number = edited_item["episode"]

    new_vid = VideoModel.get_by_id(item["id"])
    new_vid.duration = edited_item["duration"]
    new_vid.jellyfin_id = edited_item["jellyfin_id"]
    new_vid.contains_unique_content = edited_item["contains_unique_content"]
    if channel is not None:
        new_vid.channel = channel
    if youtube_series is not None:
        new_vid.youtube_series = youtube_series
    if playlist is not None:
        new_vid.playlist = playlist
    # 10/18 no idea why and im too scared to ask
    if new_series != "asdf":
        new_vid.series = new_series
    if album is not None:
        new_vid.album = album
    if episode_number is not None:
        new_vid.episode = episode_number

    new_vid.save()


@solara.component_vue("../components/video/video_table.vue", vuetify=True)
def VideoDisplayTable(
    items: list = [],
    table_title: str = "",
    hide_column: str = "",
    show_nonunique: bool = False,
    event_save_video_item=None,
    event_link1_clicked: Callable = None,
    event_link2_clicked: Callable = None,
    event_link3_clicked: Callable = None,
    event_delete_video_item: Callable = None,
):
    pass


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router)
    base_query, filter, id_to_filter, show_nonunique = create_query_from_url()
    table_title = create_table_title(filter, id_to_filter)

    if base_query is None:
        solara.Markdown("Invalid Query. Please check the URL.")
        logger.debug("No base query")
        return

    item_list = [
        VideoItem(**item.model_to_dict()).serialize()
        for item in base_query.order_by(VideoModel.upload_date.desc())
    ]

    with solara.Column(classes=["main-container"]):
        VideoDisplayTable(
            items=item_list,
            table_title=table_title,
            hide_column=filter,
            show_nonunique=show_nonunique,
            event_save_video_item=save_video_item,
            event_link1_clicked=lambda x: view_details(router, x),
            event_delete_video_item=delete_video_item,
        )
