from typing import cast
import solara
from hmtc.components.shared.sidebar import MySidebar
from hmtc.models import Video, Channel, Series, YoutubeSeries, Playlist
import peewee
import pandas as pd
from hmtc.components.cross_filter.filter_report import FilterReport
from hmtc.components.cross_filter.select import CrossFilterSelect


@solara.component_vue("sandbox.vue", vuetify=True)
def Sandbox(items: list = []):
    pass


@solara.component
def Page():
    base_query = (
        Video.select(
            Video.upload_date,
            YoutubeSeries,
            Video.episode,
            Video.title,
            Video.youtube_id,
            Video.duration,
            Channel,
            Series,
            Playlist,
            Video.id,
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
    MySidebar(router=solara.use_router())
    solara.provide_cross_filter()

    df = pd.DataFrame([item.model_to_dict() for item in base_query])
    # the 'records' key is necessary for some reason (ai thinks its a Vue)

    with solara.Column(classes=["main-container"]):
        items = df.to_dict("records")
        Sandbox(items=items)
