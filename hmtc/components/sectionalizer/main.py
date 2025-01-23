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


@solara.component
def SectionSelector(sections):
    with solara.Card():
        solara.Markdown("### Sections")
        for section in sections.value:
            with solara.Row():
                solara.Text(
                    f"{section['start_time']:.2f}s - {section['end_time']:.2f}s:"
                )


@solara.component
def SectionEditor(section):
    with solara.Card():
        solara.Markdown(f"Section Editor for section {section}")


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


def Sectionalizer():
    # State management
    video_time = solara.use_reactive(0.0)  # Current video time
    total_duration = solara.use_reactive(600.0)  # Total duration of the video
    is_editing_mode = solara.use_reactive(False)  # Editing mode state
    sections = solara.use_reactive([])
    current_section = solara.use_reactive(None)

    def update_time_cursor(new_time: float):
        # Logic to handle the updated video time
        video_time.value = new_time
        logger.debug(f"Video time updated to: {new_time}")
        # Add your logic to process the video time here

    def create_section(*args):
        start = args[0]["start"]
        end = args[0]["end"]
        logger.debug(f"Creating section from {start} to {end}")
        sections.set(sections.value + [asdict(Section(start, end))])

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
        if len(sections.value) > 0:
            with solara.Columns([4, 8]):
                SectionSelector(sections)
                if current_section.value is not None:
                    SectionEditor(current_section.value)
                else:
                    with solara.Card():
                        solara.Text(f"No section selected currently")
