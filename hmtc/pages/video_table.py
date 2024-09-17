from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Channel, Series, YoutubeSeries, Playlist
from hmtc.schemas.video import VideoItem
import peewee
import pandas as pd
from loguru import logger

force_update_counter = solara.reactive(0)


@solara.component_vue("../components/video/video_table.vue", vuetify=True)
def VideoTable(
    items: list = [],
    event_save_video_item=None,
    channels: list = [],
    selected_channel: dict = None,
    serieses: list = [],
    selected_series: dict = None,
    youtube_serieses: list = [],
    selected_youtube_series: dict = None,
    playlists: list = [],
    selected_playlist: dict = None,
    event_link_clicked: Callable = None,
    event_delete_video_item: Callable = None,
):
    pass


def delete_video_item(item):
    logger.debug(f"Deleting Item received from Vue: {item}")


def save_video_item(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    selected_channel = dict_of_items["selectedChannel"]
    selected_series = dict_of_items["selectedSeries"]
    selected_youtube_series = dict_of_items["selectedYoutubeSeries"]
    selected_playlist = dict_of_items["selectedPlaylist"]

    channel = None
    playlist = None
    youtube_series = None
    series = None

    logger.debug(f"Item received from Vue: {item}")

    video_item = VideoItem.get_by_id(item["id"])

    if selected_channel["id"] is not None:
        logger.debug(f"Selected channel: {selected_channel}")
        if selected_channel["id"] != video_item.channel.id:
            channel = Channel.get_by_id(selected_channel["id"])

            logger.debug(
                f"Channel id is different. Need to update to {selected_channel['name']} from {video_item.channel.name}"
            )

    if selected_series["id"] is not None:
        if selected_series["id"] != video_item.series.id:
            series = Series.get_by_id(selected_series["id"])

            logger.debug(
                f"selected_series id is different. Need to update to {selected_series['name']} from {video_item.series.name}"
            )

    if selected_youtube_series["id"] is not None:
        logger.debug(f"Selected youtube series: {selected_youtube_series}")
        if video_item.youtube_series is None or (
            selected_youtube_series["id"] != video_item.youtube_series.id
        ):
            logger.debug(
                f"Youtube series is None. Need to update it to {selected_youtube_series['title']}"
            )
            youtube_series = YoutubeSeries.get_by_id(selected_youtube_series["id"])

    if selected_playlist["id"] is not None:
        logger.debug(f"Selected playlist: {selected_playlist}")
        if video_item.playlist is None:
            logger.debug(
                f"Playlist is None. Need to update it to {selected_playlist['title']}"
            )
            playlist = Playlist.get_by_id(selected_playlist["id"])
        elif selected_playlist["id"] != video_item.playlist.id:
            logger.debug(
                f"Playlist id is different. Need to update to {selected_playlist['title']} from {video_item.playlist.title}"
            )
    new_vid = Video.get_by_id(item["id"])
    new_vid.duration = edited_item["duration"]
    new_vid.jellyfin_id = edited_item["jellyfin_id"]
    if edited_item["episode"] is not None:
        new_vid.episode = str(edited_item["episode"])

    if channel is not None:
        new_vid.channel = channel
    if youtube_series is not None:
        new_vid.youtube_series = youtube_series
    if playlist is not None:
        new_vid.playlist = playlist
    if series is not None:
        new_vid.series = series

    new_vid.save()
    force_update_counter.set(force_update_counter.value + 1)


def view_sections(router, item):

    router.push(f"/sections/{item['id']}")


@solara.component
def Page():
    base_query = (
        Video.select(
            Video.id,
            Video.contains_unique_content,
            Video.upload_date,
            Video.episode,
            Video.title,
            Video.youtube_id,
            Video.duration,
            Video.jellyfin_id,
            Channel,
            Series,
            Playlist,
            YoutubeSeries,
        )
        .join(Channel, peewee.JOIN.LEFT_OUTER)
        .switch(Video)
        .join(Series)
        .switch(Video)
        .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
        .switch(Video)
        .join(Playlist, peewee.JOIN.LEFT_OUTER)
        .where(Video.contains_unique_content == True)
    )
    router = solara.use_router()
    MySidebar(router)

    df = pd.DataFrame([item.model_to_dict() for item in base_query])
    channels = [
        {"id": channel.id, "name": channel.name}
        for channel in Channel.select().order_by(Channel.name)
    ]
    serieses = [
        {"id": series.id, "name": series.name}
        for series in Series.select().order_by(Series.name)
    ]
    youtube_serieses = [
        {"id": series.id, "title": series.title}
        for series in YoutubeSeries.select().order_by(YoutubeSeries.title)
    ]

    playlists = [
        {"id": playlist.id, "title": playlist.title}
        for playlist in Playlist.select().order_by(Playlist.title)
    ]

    # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
    items = df.to_dict("records")
    with solara.Column(classes=["main-container"]):
        # solara.Markdown(f"{force_update_counter.value}")
        VideoTable(
            items=items,
            event_save_video_item=save_video_item,
            channels=channels,
            selected_channel={"id": None, "name": None},
            serieses=serieses,
            selected_series={"id": None, "name": None},
            youtube_serieses=youtube_serieses,
            selected_youtube_series={"id": None, "title": None},
            playlists=playlists,
            selected_playlist={"id": None, "title": None},
            event_link_clicked=lambda x: view_sections(router, x),
            event_delete_video_item=delete_video_item,
        )
