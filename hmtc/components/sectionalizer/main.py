from dataclasses import dataclass, asdict
from typing import List
from loguru import logger
import numpy as np
import solara


@dataclass
class Section:
    start_time: float
    end_time: float = 0
    section_type: str = "unnamed"
    is_complete: bool = False


@solara.component_vue("Timeline.vue")
def Timeline(videoTime, localVideoTime, totalDuration, sections, event_update_video_time):
    pass


@solara.component
def Sectionalizer():
    # State management
    video_time = solara.use_reactive(0.0)
    local_video_time = solara.use_reactive(0.0)
    total_duration = solara.use_reactive(600.0)
    sections = solara.use_reactive([asdict(Section(0, 200))])
    current_section = solara.use_reactive(None)

    def event_update_video_time(new_time: float):
        logger.debug(f"New time {new_time}")
        if new_time is None:
            logger.error(f"{new_time} is None!!!")
            return
        video_time.value = new_time
        local_video_time.value = new_time
    
    with solara.Column(align="center"):
        solara.Markdown("## Video Sectionalizer")

        # Video player
        with solara.Card():
            solara.Text("Video Player Placeholder")

        # Timeline visualization using Vue component
        Timeline(
            videoTime=video_time.value,
            localVideoTime=local_video_time.value,
            totalDuration=total_duration.value,
            sections=sections.value,
            event_update_video_time=event_update_video_time
        )

        # Basic controls
        with solara.Row():
            solara.Button("Play/Pause", color="primary")
            if local_video_time.value is not None:
                solara.Text(f"Current Time: {local_video_time.value:.2f}s")

        # Section controls
        with solara.Row():
            solara.Button(
                "Mark Start",
                color="success",
                on_click=lambda: sections.set(sections.value + [asdict(Section(local_video_time.value))]),
            )

            solara.Button(
                "Mark End",
                color="error",
                disabled=not current_section.value or current_section.value.is_complete,
            )

        # Section list
        with solara.Card():
            solara.Markdown("### Marked Sections")
            for section in sections.value:
                with solara.Row():
                    solara.Text(
                        f"{section['start_time']:.2f}s - {section['end_time']:.2f}s:"
                    )
