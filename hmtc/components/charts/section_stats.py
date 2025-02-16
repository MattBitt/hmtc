import pandas as pd
import plotly.express as px
import solara
from loguru import logger
from peewee import fn

from hmtc.assets.icons.icon_repo import Icons
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.models import Section as SectionModel
from hmtc.models import Video as VideoModel


@solara.component_vue("./SectionStats.vue", vuetify=True)
def _SectionStats(title: str = "Domain Card", icon: str = Icons.USER.value, stats={}):
    pass


@solara.component
def SectionStats():
    video_seconds = 0
    sections_ms = 0
    ft_sections_ms = 0

    video_seconds = (
        VideoModel.select(fn.SUM(VideoModel.duration))
        .where(VideoModel.unique_content == True)
        .scalar()
    )
    video_hours = video_seconds // 3600
    logger.debug(f"{video_hours}")

    sections_ms = SectionModel.select(
        fn.SUM(SectionModel.end - SectionModel.start)
    ).scalar()
    section_hours = sections_ms // 1000 // 3600
    logger.debug(f"{section_hours}")

    ft_sections_ms = (
        SectionModel.select(fn.SUM(SectionModel.end - SectionModel.start))
        .where(SectionModel.fine_tuned == True)
        .scalar()
    )
    ft_section_hours = ft_sections_ms // 1000 // 3600
    logger.debug(f"{ft_section_hours}")

    stats = {
        "video_hours": video_hours,
        "section_hours": section_hours,
        "fine_tuned_section_hours": ft_section_hours,
    }
    _SectionStats(title="Section Stats", icon=Icons.STATS.value, stats=stats)
