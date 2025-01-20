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
def Timeline(videoTime, totalDuration, event_update_video_time):
    pass


@solara.component
def Sectionalizer():
    # State management
    video_time = solara.use_reactive(0.0)  # Current video time
    total_duration = solara.use_reactive(600.0)  # Total duration of the video
    is_editing_mode = solara.use_reactive(False)  # Editing mode state
    sections = solara.use_reactive([asdict(Section(0, 200))])
    current_section = solara.use_reactive(None)

    def update_video_time(new_time: float):
        # Logic to handle the updated video time
        video_time.value = new_time
        logger.debug(f"Video time updated to: {new_time}")
        # Add your logic to process the video time here

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Video Sectionalizer")

        # Video player
        with solara.Card():
            solara.Text("Video Player Placeholder")

        # Timeline visualization using Vue component
        Timeline(
            videoTime=video_time.value,
            totalDuration=total_duration.value,
            event_update_video_time=update_video_time,  # Pass the update function
        )

        # Basic controls
        with solara.Row():
            solara.Button("Play/Pause", color="primary")
            if video_time.value is not None:
                solara.Text(f"Current Time: {video_time.value:.2f}s")

        # Section controls
        with solara.Row():
            solara.Button(
                "Mark Start",
                color="success",
                on_click=lambda: sections.set(
                    sections.value + [asdict(Section(video_time.value))]
                ),
            )

            solara.Button(
                "Mark End",
                color="error",
                disabled=not current_section.value or current_section.value.is_complete,
            )

    with solara.Columns([4, 8]):

        with solara.Card():
            solara.Markdown("### Sections")
            for section in sections.value:
                with solara.Row():
                    solara.Text(
                        f"{section['start_time']:.2f}s - {section['end_time']:.2f}s:"
                    )
        with solara.Card():
            solara.Markdown("Section Editor")

    # Example of using the video_time in your logic
    # You can use video_time.value wherever you need the current video time
    print(f"Current video time is: {video_time.value}")
