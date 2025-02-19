import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.jf_panel import JFPanel
from hmtc.components.video.section_dialog_button import SectionDialogButton
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.utils.jellyfin_functions import (
    get_current_user_timestamp,
    jf_playpause,
    load_media_item,
    refresh_library,
    search_for_media,
)
from hmtc.utils.opencv.image_extractor import ImageExtractor
from hmtc.utils.subtitles import (
    find_closest_caption,
    find_substantial_phrase_lines,
    merge_subtitles,
    read_srt_file,
)
from hmtc.utils.time_functions import seconds_to_hms

sections = solara.reactive([])


def load_in_jellyfin(video: Video):
    logger.debug(f"Searching for {video.instance.youtube_id}")
    media = search_for_media("videos", video.instance.youtube_id)
    if media is None:
        logger.error(f"{video.instance.youtube_id} not found.")
        return
    load_media_item(media["Id"])


@solara.component_vue("./TimeSlider.vue", vuetify=True)
def TimeSlider(timeCursor, totalDuration, durationString, event_update_time_cursor):
    pass


@solara.component
def ControlPanel(
    video: Video,
    sections,
    time_cursor: solara.Reactive,
    totalDuration: int,
    durationString: str,
    event_update_time_cursor,
    event_create_section,
):

    start_time = solara.use_reactive(None)

    def create_section(start, end):
        logger.debug(f"creating section {start} {end} for {video}")

    def mark_start():
        start_time.set(time_cursor.value)

    def mark_end():
        new_section = video.create_section(start_time.value, time_cursor.value)
        sections.set(sections.value + [new_section])
        start_time.set(None)

    def cancel():
        start_time.set(None)

    def jump_to_jellyfin():
        jf_time = get_current_user_timestamp()
        if jf_time is None:
            logger.error(f"Can't get user timestamp to Jellyfin")
            return
        time_cursor.set(int(jf_time))

    def new_section():
        jf_time = get_current_user_timestamp()
        if jf_time is None:
            logger.error(f"Can't get user timestamp to Jellyfin")
            return
        if jf_time > video.instance.duration:
            logger.error(
                f"Jellyfin timestamp ({jf_time} is larger than the videos duration {video.instance.duration})"
            )

        time_cursor.set(int(jf_time))
        start_time.set(int(jf_time))

    def can_finish_section():
        if start_time.value is None:
            return False

        return (time_cursor.value - start_time.value) > 10

    with solara.Card():

        with solara.Column():
            TimeSlider(
                timeCursor=time_cursor.value,
                totalDuration=totalDuration,
                durationString=durationString,
                event_update_time_cursor=event_update_time_cursor,
            )

        with solara.Row():
            solara.Button(
                f"Jump to Jellyfin",
                on_click=jump_to_jellyfin,
                icon_name=Icons.JELLYFISH.value,
                classes=["button"],
            )

            with SwapTransition(show_first=(start_time.value is None), name="fade"):
                with solara.Column():
                    with solara.Row():
                        solara.Button(
                            "Mark Start", on_click=mark_start, classes=["button"]
                        )
                        solara.Button(
                            f"Mark Start @Jellyfin",
                            on_click=new_section,
                            icon_name=Icons.JELLYFISH.value,
                            classes=["button"],
                        )
                with solara.Column():
                    with solara.Row():
                        solara.Button(
                            "Cancel", on_click=cancel, classes=["button mywarning"]
                        )
                        solara.Button(
                            "Mark End",
                            on_click=mark_end,
                            classes=["button"],
                            disabled=(not can_finish_section()),
                        )
                        solara.Text(f"Section started at {start_time}")


@solara.component
def SubtitlesCard(time_cursor, subtitles):
    captions = merge_subtitles(subtitles)
    closest = find_closest_caption(time_cursor, captions)

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


@solara.component
def NoSubtitlesCard(video: Video):
    solara.Markdown(f"## No subtitles found for {video}")


@solara.component
def Subtitles(video, time_cursor):
    with solara.Column():
        if video.subtitles() is not None:
            SubtitlesCard(
                time_cursor=time_cursor.value,
                subtitles=video.subtitles(),
            )
        else:
            NoSubtitlesCard(video)


@solara.component
def JellyfinPanel(video, load_in_jellyfin, sections):
    with solara.Column():
        SectionDialogButton(
            video=video,
            reactive_sections=sections,
        )

        JFPanel(video)
        solara.Button(
            label="Load",
            icon_name=Icons.LOAD_MEDIA.value,
            on_click=load_in_jellyfin,
            classes=["button"],
        )
        with solara.Columns([1,1]):
            solara.Button(
                icon_name=Icons.REFRESH.value,
                on_click=refresh_library,
                classes=["button"],
            )
            solara.Button(
                icon_name=Icons.PLAYPAUSE.value,
                on_click=jf_playpause,
                classes=["button"],
            )


@solara.component
def Sectionalizer(video: Video, sections, create_section, time_cursor: solara.Reactive):

    def update_time_cursor(new_time: float):
        time_cursor.set(int(new_time))

    with solara.Card():
        with solara.Columns([9, 3]):
            with solara.Row(justify="center"):
                Subtitles(video, time_cursor)
            with solara.Row(justify="end"):
                JellyfinPanel(video, lambda: load_in_jellyfin(video), sections)

        with solara.Column():
            ControlPanel(
                video=video,
                sections=sections,
                time_cursor=time_cursor,
                totalDuration=video.instance.duration,
                durationString=seconds_to_hms(video.instance.duration),
                event_update_time_cursor=update_time_cursor,
                event_create_section=create_section,
            )
