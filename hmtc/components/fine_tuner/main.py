import time

import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import Chip, InputAndDisplay, PaginationControls
from hmtc.components.transitions.swap import SwapTransition
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.section import Section
from hmtc.domains.topic import Topic
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
def NotCompletedSectionCard(reactive_section: solara.Reactive):
    section: Section = reactive_section.value
    t = section.instance.title if section.instance.title is not None else ""
    c = section.instance.comments if section.instance.comments is not None else ""
    title = solara.use_reactive(t)
    comments = solara.use_reactive(c)
    topic_input = solara.use_reactive("")

    def update_time(start_or_end, data):

        setattr(section.instance, start_or_end, data["time"])
        section.instance.save()

    def new_title(title):
        section.instance.title = title
        section.instance.save()
        reactive_section.set(Section(section.instance.id))

    def clear_title():
        section.instance.title = None
        section.instance.save()
        reactive_section.set(Section(section.instance.id))

    def new_comments(comments):
        section.instance.comments = comments
        section.instance.save()
        reactive_section.set(Section(section.instance.id))

    def clear_comments():
        section.instance.comments = None
        section.instance.save()
        reactive_section.set(Section(section.instance.id))

    def add_topic_to_section(topic_string):
        st = section.add_topic(topic_string)
        if st is None:
            return

        reactive_section.set(Section(section.instance.id))
        topic_input.set("")

    def remove_topic(topic):
        section.remove_topic(topic)
        reactive_section.set(Section(section.instance.id))

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
    with solara.Columns([6, 6]):
        with solara.Column():
            InputAndDisplay(
                item=title, label="Title", create=new_title, remove=clear_title
            )
            InputAndDisplay(
                item=comments,
                label="Comments",
                create=new_comments,
                remove=clear_comments,
            )
        with solara.Column():
            solara.InputText(
                label="Topics", value=topic_input, on_value=add_topic_to_section
            )
            for topic in reactive_section.value.topics():
                Chip(item=f"{topic}", event_close=remove_topic)


@solara.component
def CompletedSectionCard(reactive_section: solara.Reactive):
    section: Section = reactive_section.value

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
    with solara.Row(justify="center"):
        if section.instance.title != "":
            solara.Text(f"{section.instance.title}")
    with solara.Row(justify="center"):
        if section.instance.comments != "":
            solara.Text(f"{section.instance.comments}")
    with solara.ColumnsResponsive():
        if len(section.instance.topics) > 0:
            for topic in section.topics():
                Chip(item=f"{topic}")


@solara.component
def SectionCard(section: Section):
    fine_tuned = solara.use_reactive(section.instance.fine_tuned)
    reactive_section = solara.use_reactive(section)

    def lock():
        if section.instance.title == "" or section.instance.title is None:
            section.instance.title = section.my_title()

        if section.my_title() is None:
            logger.error(
                f"No Title or Topics entered for this section. Can't create a title from nothing."
            )
            return

        section.instance.fine_tuned = True
        section.instance.save()
        fine_tuned.set(True)

    def unlock():
        logger.debug(f"If there are tracks then theyll need to be deleted.")
        section.instance.fine_tuned = False
        section.instance.save()
        fine_tuned.set(False)

    with SwapTransition(show_first=fine_tuned.value, name="fade"):
        CompletedSectionCard(reactive_section)
        NotCompletedSectionCard(reactive_section)

    with solara.Row(justify="center"):
        with SwapTransition(show_first=fine_tuned.value, name="fade"):
            solara.Button(
                label="Unlock",
                classes=["mywarning"],
                on_click=unlock,
                icon_name=Icons.UNLOCK.value,
            )
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
                # JFPanel(video)


@solara.component
def FineTuner(video: Video):
    current_page = solara.use_reactive(1)
    # 2/21/25
    # having issues with frontend updating between page loads
    # essentially disabling pagination here
    # at least until a video has > 16 sections...
    per_page = 16
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
