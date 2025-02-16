import solara
from loguru import logger
from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.utils.time_functions import seconds_to_hms
from hmtc.components.transitions.swap import SwapTransition

@solara.component_vue("./TimePanel.vue", vuetify=True)
def TimePanel(
    initialTime=1000, sectionID=18, video_duration=1000, event_update_time=None
):
    pass


@solara.component
def NotCompletedSectionCard(section):

    def update_time(start_or_end, data):
        logger.debug(f"Updating section {section} {start_or_end}")
        logger.debug(f"with data: {data}")

    with solara.Columns():
        TimePanel(
            initialTime=section.instance.start,
            event_update_time=lambda x: update_time("start", x),
        )
        TimePanel(
            initialTime=section.instance.end,
            event_update_time=lambda x: update_time("end", x),
        )


@solara.component
def CompletedSectionCard(section):
    
    with solara.Row(justify="center"):
        start = seconds_to_hms(section.instance.start // 1000)
        end = seconds_to_hms(section.instance.end // 1000)
        solara.Text(f"{start} - {end}", classes=["seven-seg myprimary"])


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
            classes=['mywarning'],
            on_click=unlock,
            icon_name=Icons.UNLOCK.value,
        )
        else:
            solara.Button(
            label="Finished",
            classes=['myprimary'],
            on_click=lock,
            icon_name=Icons.LOCK.value,
        )


@solara.component
def FineTuner(video: Video):
    current_page = solara.use_reactive(1)
    per_page = 3
    solara.Markdown(f"## {video.instance.title}")
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
