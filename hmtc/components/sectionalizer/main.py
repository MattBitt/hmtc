import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import solara
from loguru import logger

from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.section_dialog_button import SectionDialogButton
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.subtitles import (
    find_closest_caption,
    find_substantial_phrase_lines,
    merge_subtitles,
    read_srt_file,
)
from hmtc.utils.time_functions import seconds_to_hms


@dataclass
class Topic:
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid1()))


@solara.component_vue("CoarseAdjust.vue", vuetify=True)
def CoarseAdjust(
    videoTime,
    totalDuration,
    durationString,
    event_update_time_cursor,
    event_create_section,
):
    pass


@solara.component_vue("BarGraph.vue", vuetify=True)
def BarGraph(possibles):
    pass


@solara.component
def VideoFrame(video: Video, time_cursor):
    vid_file = video.video_file()
    try:
        ie = ImageExtractor(vid_file)
        frame = ie.extract_frame(time_cursor / 1000)
    except Exception as e:
        logger.error(f"Error {e}")
        return None

    solara.Image(frame, width="300px")


@solara.component
def SubtitlesCard(time_cursor, subtitles, starts_and_ends):
    searching = solara.use_reactive(False)

    captions = merge_subtitles(subtitles)

    def search_for_starts_and_ends():
        searching.set(True)
        starts = find_substantial_phrase_lines(
            captions, ["yeah", "yea", "yes", "yep", "ok", "okay", "come on"]
        )
        ends = find_substantial_phrase_lines(captions, ["let's go", "lets go"])
        starts_and_ends.set({"starts": starts, "ends": ends})
        searching.set(False)

    closest = find_closest_caption(time_cursor / 1000, captions)
    if closest is None:
        logger.error(f"Captions not found in {closest}")
        return

    while len(closest["captions"]) < 7:
        closest["captions"].append({"text": "----", "start": 0, "end": 0})
    with solara.Columns([8, 4]):
        with solara.Column():
            for index, caption in enumerate(closest["captions"]):
                if index == closest["highlight_index"]:
                    _classes = ["info--text"]
                else:
                    _classes = ["primary--text"]
                solara.Text(f"{caption['text']}", classes=_classes)

        with SwapTransition(
            show_first=starts_and_ends.value["starts"] == [], name="fade"
        ):
            BeforeSearch(search_for_starts_and_ends)
            AfterSearch(starts_and_ends)


def AfterSearch(starts_and_ends):
    with solara.Column():
        possibles = []
        for starts in starts_and_ends.value["starts"]:
            possibles.append(starts.start)
        seconds = [p.seconds for p in possibles]
        solara.Text(f"Possibles", classes=["primary--text"])
        for sec in seconds:
            with solara.Row():
                solara.Text(f"{seconds_to_hms(sec)} ({sec})", classes=["info--text"])


def BeforeSearch(search_for_starts_and_ends):
    with solara.Column():
        solara.Button(
            f"Start/Ends",
            on_click=search_for_starts_and_ends,
            classes=["button"],
        )


sections = solara.reactive([])


@solara.component
def Sectionalizer(video, create_section):
    # session = solara.get_session_id()
    # logger.debug(f"Loading sectionalizer. Current session {session}")
    time_cursor = solara.use_reactive(0)  # Current video time
    video_duration_ms = solara.use_reactive(
        video.instance.duration * 1000
    )  # Total duration of the video

    def update_time_cursor(new_time: float):
        time_cursor.value = new_time

    _raw_sections = Section.get_for_video(video.instance.id)
    _sections = [s.serialize() for s in _raw_sections]
    sections = solara.use_reactive(_sections)

    possibles = solara.use_reactive({"starts": [], "ends": []})

    with solara.Card(video.instance.title):
        with solara.Columns([6, 6]):
            with solara.Column():
                if video.video_file() is not None:
                    with solara.Column():
                        with solara.Row(justify="center"):
                            VideoFrame(video=video, time_cursor=time_cursor.value)

                else:
                    solara.Markdown(
                        f"## No Video (think mkv) file Found for {video.instance}"
                    )
            with solara.Column():
                subtitles = video.subtitles()
                if subtitles is not None:
                    SubtitlesCard(
                        time_cursor=time_cursor.value,
                        subtitles=subtitles,
                        starts_and_ends=possibles,
                    )
                else:
                    solara.Markdown(f"No subtitles found for {video.instance.title}")

        with solara.Row(justify="center"):
            SectionDialogButton(
                video=video,
                reactive_sections=sections,
            )
            solara.Text(
                seconds_to_hms(int(time_cursor.value / 1000)),
                classes=["seven-seg"],
            )
        with solara.Column():
            times = [p.start.seconds for p in possibles.value["starts"]]
            with SwapTransition(show_first=(len(times) > 0), name="slide-fade"):
                BarGraph(possibles=times)
                solara.Text(f"No search performed yet.")
            CoarseAdjust(
                videoTime=time_cursor.value,
                totalDuration=video_duration_ms.value,
                durationString=seconds_to_hms(int(video_duration_ms.value / 1000)),
                event_update_time_cursor=update_time_cursor,
                event_create_section=create_section,
            )
