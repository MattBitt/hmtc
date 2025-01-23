from dataclasses import asdict, dataclass
from typing import List

import numpy as np
import solara
from loguru import logger


@dataclass
class Section:
    start_time: float
    end_time: float = 0
    section_type: str = "unnamed"
    is_complete: bool = False


@solara.component_vue("Timeline.vue")
def Timeline(videoTime, totalDuration, event_update_time_cursor, event_create_section):
    pass


@solara.component_vue("SectionSelector.vue")
def SectionSelector(sections, selected, event_set_selected):
    pass


@solara.component
def VideoFrame(video_time):
    with solara.Card():
        solara.Text("Video Player Placeholder")
        solara.Text(f"{video_time}")


@solara.component
def SubtitlesCard(video_time):
    with solara.Card():
        solara.Text("Subtitles")
        solara.Text(f"{video_time}")


sections = solara.reactive([])
current_section = solara.reactive(None)


@solara.component
def SectionRow(sections, current_section):

    def select_section(selected_section):
        current_section.set(selected_section)

    with solara.Column():
        SectionSelector(
            sections=sections.value,
            selected=current_section.value,
            event_set_selected=select_section,
        )


@solara.component
def Sectionalizer():
    # State management
    video_time = solara.use_reactive(0.0)  # Current video time
    total_duration = solara.use_reactive(600.0)  # Total duration of the video

    def update_time_cursor(new_time: float):
        # Logic to handle the updated video time
        video_time.value = new_time
        logger.debug(f"Video time updated to: {new_time}")
        # Add your logic to process the video time here

    def create_section(*args):
        start = args[0]["start"]
        end = args[0]["end"]
        logger.debug(f"Creating section from {start} to {end}")
        new_sect = asdict(Section(start, end))
        sections.set(sections.value + [new_sect])

    with solara.Column(classes=["main-container"]):
        with solara.Columns():
            VideoFrame(video_time.value)
            SubtitlesCard(video_time.value)

        Timeline(
            videoTime=video_time.value,
            totalDuration=total_duration.value,
            event_update_time_cursor=update_time_cursor,
            event_create_section=create_section,
        )
        solara.Markdown(f"Currently Selected {current_section.value}")
        if len(sections.value) > 0:
            SectionRow(sections, current_section)
