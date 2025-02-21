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
def _SectionStats(title: str = "_SectionStats", icon: str = Icons.USER.value, stats={}):
    pass


def scalar_or_0(query):
    res = query.scalar()
    if res is None:
        return 0
    else:
        return res


@solara.component
def SectionStats():
    non_unique_video_seconds = scalar_or_0(
        VideoModel.select(fn.SUM(VideoModel.duration)).where(
            VideoModel.unique_content == False
        )
    )
    logger.debug(f"{non_unique_video_seconds=}")
    non_unique_video_hours = non_unique_video_seconds // 3600
    logger.debug(f"{non_unique_video_hours=}")

    video_seconds = scalar_or_0(
        VideoModel.select(fn.SUM(VideoModel.duration)).where(
            VideoModel.unique_content == True
        )
    )
    logger.debug(f"{video_seconds=}")
    video_hours = video_seconds // 3600
    logger.debug(f"{video_hours=}")

    sections_ms = scalar_or_0(
        SectionModel.select(fn.SUM(SectionModel.end - SectionModel.start)).where(
            SectionModel.video_id.in_(
                VideoModel.select(VideoModel.id).where(
                    VideoModel.unique_content == True
                )
            )
        )
    )
    logger.debug(f"{sections_ms=}")
    section_hours = sections_ms // 1000 // 3600
    logger.debug(f"{section_hours=}")
    videos_with_sections_seconds = scalar_or_0(
        VideoModel.select(fn.SUM(VideoModel.duration)).where(
            (VideoModel.unique_content == True)
            & (VideoModel.id.in_(SectionModel.select(SectionModel.video_id)))
        )
    )

    non_musical_section_seconds = videos_with_sections_seconds - (sections_ms / 1000)
    logger.debug(f"{non_musical_section_seconds=}")
    non_musical_section_hours = non_musical_section_seconds // 3600
    logger.debug(f"{non_musical_section_hours=}")

    ft_sections_ms = scalar_or_0(
        SectionModel.select(fn.SUM(SectionModel.end - SectionModel.start)).where(
            SectionModel.fine_tuned == True
        )
    )
    if ft_sections_ms is not None:
        ft_section_hours = ft_sections_ms // 1000 // 3600
    else:
        ft_section_hours = 0

    stats = {
        "non_unique_video_hours": non_unique_video_hours,
        "non_musical_section_hours": non_musical_section_hours,
        "video_hours": video_hours,
        "section_hours": section_hours,
        "fine_tuned_section_hours": ft_section_hours,
    }
    logger.debug(f"calling stats with {stats}")
    _SectionStats(title="Section Stats", icon=Icons.STATS.value, stats=stats)
