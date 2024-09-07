import plotly
import solara
import solara.lab
import peewee
from typing import Any, Dict, List, Optional, cast
import ipyvuetify
import pandas as pd
import traitlets
import reacton.ipyvuetify as v
from loguru import logger
from hmtc.models import Video, Channel, Series, YoutubeSeries, Playlist
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.cross_filter.filter_report import FilterReport
from hmtc.components.cross_filter.select import CrossFilterSelect
from hmtc.components.cross_filter.dataframe import FilteredDataFrame

base_query = (
    Video.select(
        Video.upload_date,
        YoutubeSeries.title.alias("yts_title"),
        Video.episode,
        Video.title,
        Video.youtube_id,
        Video.duration,
        Channel.name.alias("channel_name"),
        Series.name.alias("series_name"),
        Playlist.title.alias("playlist_title"),
        Video.id.alias("video_id"),
        Series.id.alias("series_id"),
        Channel.id.alias("channel_id"),
        Playlist.id.alias("playlist_id"),
        Video.contains_unique_content,
    )
    .join(Channel, peewee.JOIN.LEFT_OUTER)
    .switch(Video)
    .join(Series)
    .switch(Video)
    .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
    .switch(Video)
    .join(Playlist, peewee.JOIN.LEFT_OUTER)
)


@solara.component
def Page():
    sort_by_name = solara.use_reactive(False)
    sort_by_duration = solara.use_reactive(False)

    MySidebar(router=solara.use_router())

    mydata = solara.use_reactive(
        [
            {"name": "fdasewr", "age": 123},
            {"name": "fdsfdasewr", "age": 23},
            {"name": "qfqdasewr", "age": 12},
            {"name": "dfyuuyasewr", "age": 1243},
            {"name": "lkjhlfdasewr", "age": 1923},
            {"name": "sadfghsewr", "age": 1236},
        ]
    )

    mydata2 = solara.use_reactive(
        list(base_query.order_by(Video.upload_date.desc()).dicts())
    )

    def sort_name():
        nonlocal mydata
        if sort_by_name.value:
            mydata.value = sorted(
                mydata.value,
                key=lambda x: x["name"],
                reverse=True,
            )

        else:
            mydata.value = sorted(
                mydata.value,
                key=lambda x: x["name"],
                reverse=False,
            )

        sort_by_name.set(not sort_by_name.value)

    def sort_duration():
        nonlocal mydata2
        mydata2.value = sorted(
            mydata2.value,
            key=lambda x: x["duration"],
            reverse=not sort_by_duration.value,
        )
        sort_by_duration.set(not sort_by_duration.value)

    # query = solara.use_reactive(base_query.order_by(Video.duration.desc()).dicts())
    df = pd.DataFrame(mydata2.value)
    solara.provide_cross_filter()
    with solara.Column(classes=["main-container"]):
        with solara.Card():
            with solara.Row(gap=16):
                CrossFilterSelect(df, "yts_title")
                CrossFilterSelect(df, "channel_name")
                CrossFilterSelect(df, "series_name")
                CrossFilterSelect(
                    df,
                    "contains_unique_content",
                )
                FilterReport(df)

        FilteredDataFrame(df)

        with solara.Column():
            solara.Markdown(f"Sort By Duration: {sort_by_duration.value}")
            solara.Button("Sort", on_click=sort_duration)
