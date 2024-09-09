from typing import cast, Callable
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Channel, Series, YoutubeSeries, Playlist
from hmtc.schemas.video import VideoItem
import peewee
import pandas as pd
from loguru import logger


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
):
    pass


def save_video_item(dict_of_items):
    item = dict_of_items["item"]
    edited_item = dict_of_items["editedItem"]
    selected_channel = dict_of_items["selectedChannel"]
    selected_series = dict_of_items["selectedSeries"]
    selected_youtube_series = dict_of_items["selectedYoutubeSeries"]

    logger.debug(f"Item received from Vue: {item}")

    video_item = VideoItem.get_by_id(item["id"])

    if selected_channel["id"] is not None:
        logger.debug(f"Selected channel: {selected_channel}")
        if selected_channel["id"] != video_item.channel.id:
            logger.debug(
                f"Channel id is different. Need to update to {selected_channel['name']} from {video_item.channel.name}"
            )
    if selected_series["id"] is not None:
        logger.debug(f"Selected series: {selected_series}")

    if selected_youtube_series["id"] is not None:
        logger.debug(f"Selected youtube series: {selected_youtube_series}")
        if video_item.youtube_series is None:
            logger.debug(
                f"Youtube series is None. Need to update it to {selected_youtube_series['title']}"
            )
            return
        if selected_youtube_series["id"] != video_item.youtube_series.id:
            logger.debug(
                f"Youtube series id is different. Need to update to {selected_youtube_series['title']} from {video_item.youtube_series.title}"
            )

    logger.debug(f"Video item: {video_item}")


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
    MySidebar(router=solara.use_router())

    df = pd.DataFrame([item.model_to_dict() for item in base_query])

    with solara.Column(classes=["main-container"]):
        # the 'records' key is necessary for some reason (ai thinks its a Vue thing)
        items = df.to_dict("records")
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
        VideoTable(
            items=items,
            event_save_video_item=save_video_item,
            channels=channels,
            selected_channel={"id": None, "name": None},
            serieses=serieses,
            selected_series={"id": None, "name": None},
            youtube_serieses=youtube_serieses,
            selected_youtube_series={"id": None, "title": None},
        )
