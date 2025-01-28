import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import solara
from loguru import logger

from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.subtitles import (
    find_closest_caption,
    find_substantial_phrase_lines,
    read_vtt,
)


@dataclass
class Topic:
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid1()))


@dataclass
class Section:
    start: float
    end: float = 0
    id: str = field(default_factory=lambda: str(uuid.uuid1()))
    section_type: str = "unnamed"
    is_complete: bool = False
    topics = []


@solara.component_vue("Timeline.vue")
def Timeline(videoTime, totalDuration, event_update_time_cursor, event_create_section):
    pass


@solara.component_vue("SectionSelector.vue")
def SectionSelector(
    sections, selected, video_duration, event_remove_section, event_update_selected
):
    pass


@solara.component
def VideoFrame(video, time_cursor):
    vid_file = video.video_file()
    try:
        ie = ImageExtractor(vid_file)
        frame = ie.extract_frame(time_cursor / 1000)
    except Exception as e:
        logger.error(f"Error {e}")
        return None
    
    solara.Image(frame, width="300px")


@solara.component
def SubtitlesCard(time_cursor, subtitles):
    searching = solara.use_reactive(False)
    starts_and_ends = solara.use_reactive({})

    def search_for_starts_and_ends():
        searching.set(True)
        starts = find_substantial_phrase_lines(
            captions, ["yeah", "yea", "yes", "yep", "ok", "okay"]
        )
        ends = find_substantial_phrase_lines(captions, ["let's go", "lets go"])
        starts_and_ends.set({"starts": starts, "ends": ends})
        searching.set(False)

    captions = read_vtt(subtitles)
    closest = find_closest_caption(time_cursor / 1000, captions)
    solara.Button(
        f"Search for Start/Ends",
        on_click=search_for_starts_and_ends,
        classes=["button"],
    )
    for index, caption in enumerate(closest["captions"]):
        if index == closest["highlight_index"]:
            _classes = ["info--text"]
        else:
            _classes = ["primary--text"]
        solara.Text(f"{caption['text']}", classes=_classes)
    if starts_and_ends.value != {}:
        solara.Markdown(f"Starts found: {starts_and_ends.value['starts']}")
        solara.Markdown(f"Ends found: {starts_and_ends.value['ends']}")


sections = solara.reactive([])
selected = solara.reactive({})


@solara.component
def Sectionalizer(video):
    # State management
    time_cursor = solara.use_reactive(0)  # Current video time
    video_duration_ms = solara.use_reactive(
        video.instance.duration * 1000
    )  # Total duration of the video

    def update_time_cursor(new_time: float):
        # Logic to handle the updated video time
        time_cursor.value = new_time
        logger.debug(f"Video time updated to: {new_time}")
        # Add your logic to process the video time here

    def update_selected(section):
        selected.set(section)

    def create_section(*args):
        start = args[0]["start"]
        end = args[0]["end"]
        logger.debug(f"Creating section from {start} to {end}")
        _section = Section(start, end)
        _topics = [
            asdict(t)
            for t in (
                Topic("banana"),
                Topic("pineapple"),
                Topic("hippo"),
                Topic("table"),
            )
        ]
        new_sect = asdict(_section)
        new_sect["topics"] = _topics
        sections.set(sections.value + [new_sect])
        logger.debug(f"After Creating section from {start} to {end}")

    def remove_section(section):
        logger.debug(f"Remove section {section}")
        a = []
        a[:] = [d for d in sections.value if d.get("id") != section["id"]]
        sections.set(a)

    with solara.Card("Sectionalizer"):
        with solara.Columns():
            if video.video_file() is None:
                solara.Markdown(
                    f"## No Video (think mkv) file Found for {video.instance}"
                )
            else:
                VideoFrame(video=video, time_cursor=time_cursor.value)

            subtitles = video.subtitles()
            if subtitles is not None:
                SubtitlesCard(time_cursor=time_cursor.value, subtitles=subtitles)
            else:
                solara.Markdown(f"No subtitles found for {video.instance.title}")
        Timeline(
            videoTime=time_cursor.value,
            totalDuration=video_duration_ms.value,
            event_update_time_cursor=update_time_cursor,
            event_create_section=create_section,
        )

        if len(sections.value) > 0:
            with solara.Column():
                SectionSelector(
                    sections=sections.value,
                    selected=selected.value,
                    video_duration=video_duration_ms.value,
                    event_update_selected=update_selected,
                    event_remove_section=remove_section,
                )
