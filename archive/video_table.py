import solara
import solara.lab
import peewee
from typing import Any, Dict, Optional, cast
import pandas as pd
from hmtc.models import VideoModel, Channel, Series, YoutubeSeries, Playlist
from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.cross_filter.filter_report import FilterReport
from hmtc.components.cross_filter.select import CrossFilterSelect
from hmtc.components.cross_filter.dataframe import FilteredDataFrame


# Memoized sorting function
# @lru_cache(maxsize=None)
def memoized_sort(data, column, ascending):
    data_list = [d for d in data if d[column] is not None]
    _sorted = sorted(data_list, key=lambda x: x[column], reverse=(not ascending))
    return _sorted


base_query = (
    VideoModel.select(
        VideoModel.upload_date,
        YoutubeSeries.title.alias("yts_title"),
        VideoModel.episode,
        VideoModel.title,
        VideoModel.youtube_id,
        VideoModel.duration,
        Channel.name.alias("channel_name"),
        Series.name.alias("series_name"),
        Playlist.title.alias("playlist_title"),
        VideoModel.id.alias("video_id"),
        Series.id.alias("series_id"),
        Channel.id.alias("channel_id"),
        Playlist.id.alias("playlist_id"),
        VideoModel.contains_unique_content,
    )
    .join(Channel, peewee.JOIN.LEFT_OUTER)
    .switch(VideoModel)
    .join(Series)
    .switch(VideoModel)
    .join(YoutubeSeries, peewee.JOIN.LEFT_OUTER)
    .switch(VideoModel)
    .join(Playlist, peewee.JOIN.LEFT_OUTER)
)


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    solara.use_reactive(
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
        list(base_query.order_by(VideoModel.upload_date.desc()).dicts())
    )

    column, set_column = solara.use_state(cast(Optional[str], None))
    ascending, set_ascending = solara.use_state(cast(bool, True))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))

    def on_action_column(column):
        set_column(column)

    def on_action_cell(column, row_index):
        set_cell(dict(column=column, row_index=row_index))

    column_actions = [
        solara.ColumnAction(
            icon="mdi-sunglasses", name="User column action", on_click=on_action_column
        )
    ]
    cell_actions = [
        solara.CellAction(
            icon="mdi-white-balance-sunny",
            name="User cell action",
            on_click=on_action_cell,
        )
    ]
    if column is not None:
        sorted_data = memoized_sort(mydata2.value, column, ascending)
        # Convert back to list of dictionaries
        mydata2.value = [dict(d) for d in sorted_data]

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

        FilteredDataFrame(df, column_actions=column_actions, cell_actions=cell_actions)
