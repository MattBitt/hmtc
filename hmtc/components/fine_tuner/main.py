import time

import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.utils.jellyfin_functions import (
    jf_pause,
    jf_play,
    jf_playpause,
    jf_seek_to,
    load_media_item,
    refresh_library,
    search_for_media,
)
from hmtc.utils.time_functions import seconds_to_hms


@solara.component_vue("./TimePanel.vue", vuetify=True)
def TimePanel(
    initialTime=1000,
    enable_jellyfin=False,
    video_duration=1000,
    event_update_time=None,
    event_loop_jellyfin_at=None,
):
    pass


def loop_jellyfin(args):
    logger.debug(f"with data: {args}")
    jf_seek_to(args * 10000)
    time.sleep(0.250)
    jf_playpause()
    time.sleep(0.8)
    jf_playpause()
    time.sleep(0.250)
    jf_seek_to(args * 10000)


@solara.component
def NotCompletedSectionCard(section):

    def update_time(start_or_end, data):
        logger.debug(f"Updating section {section} {start_or_end}")
        logger.debug(f"with data: {data}")
        setattr(section.instance, start_or_end, data["time"])
        section.instance.save()

    with solara.Columns():
        TimePanel(
            initialTime=section.instance.start,
            video_duration=section.instance.video.duration,
            enable_jellyfin=True,
            event_update_time=lambda x: update_time("start", x),
            event_loop_jellyfin_at=loop_jellyfin,
        )
        TimePanel(
            initialTime=section.instance.end,
            video_duration=section.instance.video.duration,
            enable_jellyfin=True,
            event_update_time=lambda x: update_time("end", x),
            event_loop_jellyfin_at=loop_jellyfin,
        )


@solara.component
def CompletedSectionCard(section):

    with solara.Row(justify="center"):
        start = seconds_to_hms(section.instance.start // 1000)
        end = seconds_to_hms(section.instance.end // 1000)
        solara.Button(
            icon_name="mdi-play",
            classes=["button"],
            on_click=lambda: loop_jellyfin(section.instance.start),
        )
        solara.Text(f"{start} - {end}", classes=["seven-seg myprimary"])
        solara.Button(
            icon_name="mdi-play",
            classes=["button"],
            on_click=lambda: loop_jellyfin(section.instance.end),
        )


@solara.component
def SectionCard(section):
    fine_tuned = solara.use_reactive(section.instance.fine_tuned)

    def lock():
        section.instance.fine_tuned = True
        section.instance.save()
        fine_tuned.set(True)

    def unlock():
        logger.debug(f"If there are tracks then theyll need to be deleted.")
        section.instance.fine_tuned = False
        section.instance.save()
        fine_tuned.set(False)

    with SwapTransition(show_first=fine_tuned.value, name="fade"):
        CompletedSectionCard(section)
        NotCompletedSectionCard(section)

    with solara.Row(justify="center"):
        if fine_tuned.value:
            solara.Button(
                label="Unlock",
                classes=["mywarning"],
                on_click=unlock,
                icon_name=Icons.UNLOCK.value,
            )
        else:
            solara.Button(
                label="Finished",
                classes=["myprimary"],
                on_click=lock,
                icon_name=Icons.LOCK.value,
            )


@solara.component
def HeaderRow(video):

    def load_in_jellyfin():
        logger.error(f"Searching for {video.instance.youtube_id}")
        media = search_for_media("videos", video.instance.youtube_id)
        if media is None:
            logger.error(f"{video.instance.youtube_id} not found.")
            return
        load_media_item(media["Id"])

    def jellyfin_refresh_library():
        refresh_library()

    with solara.Row():
        with solara.Columns([3, 9]):
            with solara.Row(justify="center"):
                with solara.Column():
                    solara.Markdown(f"##### {video.instance.title[:80]}")
                    solara.Markdown(f"###### {video.instance.duration}")
                    solara.Markdown(f"###### {seconds_to_hms(video.instance.duration)}")
            with solara.Row(justify="end"):
                solara.Button(
                    label="Load",
                    icon_name=Icons.LOAD_MEDIA.value,
                    on_click=load_in_jellyfin,
                    classes=["button"],
                )
                solara.Button(
                    label="Refresh",
                    icon_name=Icons.REFRESH.value,
                    on_click=jellyfin_refresh_library,
                    classes=["button"],
                )
                solara.Button(
                    icon_name=Icons.PLAYPAUSE.value,
                    on_click=lambda: jf_playpause(),
                    classes=["button"],
                )
                JFPanel(video)


@solara.component
def FineTuner(video: Video):
    current_page = solara.use_reactive(1)
    per_page = 2
    HeaderRow(video)
    sections, num_sections, num_pages = video.sections_paginated(
        current_page=current_page, per_page=per_page
    )

    for sect in sections:
        with solara.Card():
            section = Section(sect)
            SectionCard(section)

    PaginationControls(
        current_page=current_page, num_pages=num_pages, num_items=num_sections
    )
