import solara
from loguru import logger

from hmtc.components.shared.pagination_controls import PaginationControls
from hmtc.domains.section import Section
from hmtc.domains.video import Video
from hmtc.utils.time_functions import seconds_to_hms


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
    with solara.Card():
        with solara.Row(justify="center"):
            start = seconds_to_hms(section.instance.start // 1000)
            end = seconds_to_hms(section.instance.end // 1000)
            solara.Text(f"{start} - {end}", classes=["seven-seg myprimary"])


@solara.component
def SectionCard(section):
    fine_tuned = solara.use_reactive(section.instance.fine_tuned)

    def toggle_fine_tuned():
        section.instance.fine_tuned = not fine_tuned.value
        section.instance.save()
        fine_tuned.set(not fine_tuned.value)

    if fine_tuned.value:
        CompletedSectionCard(section)
    else:
        NotCompletedSectionCard(section)
    with solara.Row(justify="center"):
        solara.Button(
            label=f"Mark Completed {section.instance.fine_tuned}",
            classes=["button"],
            on_click=toggle_fine_tuned,
        )


@solara.component
def FineTuner(video: Video):
    current_page = solara.use_reactive(1)
    per_page = 3
    solara.Markdown(f"Video Fine Tuner")
    solara.Markdown(f"{video.instance.title}")
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
