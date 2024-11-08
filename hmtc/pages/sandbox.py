import dataclasses
import re
from pathlib import Path
from typing import Dict, Optional, cast

import plotly.graph_objects as go
import solara
from loguru import logger
from peewee import fn
from solara.alias import rv

from hmtc.components.GOBY.example_plotly_fig import PlotlyFigureComponent
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import File as FileModel
from hmtc.models import Section as SectionModel
from hmtc.models import Series as SeriesModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.track import TrackItem
from hmtc.utils.jellyfin_functions import get_current_user_timestamp


@solara.component_vue("sandbox.vue", vuetify=True)
def Sandbox():
    pass


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    unique_videos = (
        VideoModel.select(VideoModel.id)
        .where(VideoModel.contains_unique_content == True)
        .distinct()
    )
    videos_with_sections = [
        x.video_id for x in SectionModel.select(SectionModel.video_id).distinct()
    ]
    videos_with_no_sections = [
        video.id for video in unique_videos if video.id not in videos_with_sections
    ]
    logger.error(f"unique_videos: {len(unique_videos)}")
    logger.error(f"videos_with_sections: {len(videos_with_sections)}")
    logger.error(f"videos_with_no_sections: {len(videos_with_no_sections)}")

    query1 = (
        VideoModel.select(
            VideoModel.series_id,
            fn.Sum(VideoModel.duration).alias("total_duration"),
        )
        .where(VideoModel.id.in_(unique_videos))
        .group_by(VideoModel.series_id)
    )
    query2 = (
        VideoModel.select(
            VideoModel.series_id,
            fn.Sum(VideoModel.duration).alias("total_duration"),
        )
        .where(VideoModel.id.in_(videos_with_sections))
        .group_by(VideoModel.series_id)
    )
    query3 = (
        VideoModel.select(
            VideoModel.series_id,
            fn.Sum(VideoModel.duration).alias("total_duration"),
        )
        .where(VideoModel.id.in_(videos_with_no_sections))
        .group_by(VideoModel.series_id)
    )
    query4 = (
        SectionModel.select(
            fn.Sum(SectionModel.end - SectionModel.start).alias("duration")
        )
        .where(SectionModel.video_id.in_(videos_with_sections))
        .scalar()
    )

    durations = [(query.series_id, query.total_duration) for query in query1]
    durations2 = [(query.series_id, query.total_duration) for query in query2]
    durations3 = [(query.series_id, query.total_duration) for query in query3]

    videos_with_sections_duration = sum([duration[1] / 3600 for duration in durations2])
    sections_duration = query4 / 1000 / 3600
    with solara.Column():
        solara.Markdown(
            f"Total Duration (query1): {sum([duration[1] / 3600 for duration in durations])} hours"
        )
        solara.Markdown(
            f"Total Duration (query3): {sum([duration[1] / 3600 for duration in durations3])} hours"
        )
        solara.Markdown(
            f"Videos with Sections (total duration) {videos_with_sections_duration} hours"
        )

        solara.Markdown(f"Sections created (all): {sections_duration} hours")
        solara.Markdown(
            f"Music to total Ratio: {sections_duration / videos_with_sections_duration} hours"
        )
        # for duration in durations:

        #     solara.Markdown(f"Series: {duration[0]} duration: {duration[1]}")

        source = [0, 0, 1, 1]
        target = [1, 2, 3, 4]
        count = [
            videos_with_sections_duration,
            sum([duration[1] / 3600 for duration in durations3]),
            sections_duration,
            videos_with_sections_duration - sections_duration,
        ]
        nodes = [
            "videos",
            "analyzed",
            "not analyzed",
            "instrumentals",
            "non-instrumentals",
        ]
        series_list = [x for x in SeriesModel.select(SeriesModel.id, SeriesModel.name)]
        source += [3 for _ in range(len(series_list))]
        target += [4 + series.id for series in series_list]
        nodes += [series.name for series in series_list]
        for series in series_list:
            for record in durations2:
                if record[0] == series.id:
                    count.append(record[1] / 3600)
                    break

        series_counts = [x.total_duration for x in query3]

        fig = go.Figure(
            data=[
                go.Sankey(
                    node={"label": nodes},
                    link={"source": source, "target": target, "value": count},
                )
            ]
        )
        solara.FigurePlotly(fig)
