from typing import Callable

import solara
from loguru import logger

from hmtc.domains.section import Section
from hmtc.domains.video import Video


@solara.component_vue("./SectionSelector.vue", vuetify=True)
def SectionSelector(
    sections, selected, video_duration, event_remove_section, event_update_selected
):
    pass


@solara.component
def Page(video: Video, sections):


    selected = solara.use_reactive(None)

    def create_section(section):
        logger.debug(f"Creating a section for {video} using args {section}")
        start = section["start"]
        end = section["end"]
        logger.debug(f"Creating section from {start} to {end}")
        _section = Section.create(
            {
                "start": start,
                "end": end,
                "section_type": "instrumental",
                "video_id": video.instance.id,
            }
        )

        sections.set(sections.value + [_section.serialize()])
        logger.debug(f"After Creating section from {start} to {end}")

    def update_selected(section):
        selected.set(section)

    def remove_section(section):
        _sect = Section.get_by(id=section["id"])
        logger.debug(f"Remove section {_sect}")
        _sect.delete()
        a = []
        a[:] = [d for d in sections.value if d.get("id") != section["id"]]
        sections.set(a)

    SectionSelector(
        sections=sections.value,
        selected=selected.value,
        video_duration=video.instance.duration * 1000,
        event_create_section=create_section,
        event_update_selected=update_selected,
        event_remove_section=remove_section,
    )
