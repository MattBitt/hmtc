from pathlib import Path

import solara
from loguru import logger

from hmtc.domains.section import Section


@solara.component_vue("../section/SectionControlPanel.vue", vuetify=True)
def SectionControlPanel(
    video,
    jellyfin_status,
    event_delete_all_sections,
    event_create_section,
):
    pass


@solara.component
def SectionDialogButton(video, reactive_sections):
    _video = video

    def delete_all_sections(*args):
        logger.error(f"Deleting all Sections {args}")

    def create_section(section_dict):

        logger.error(f"Create Section {section_dict} for {_video.instance}")
        section_dict["section_type"] = "instrumental"
        section_dict["video_id"] = _video.instance.id
        new_section = Section.create(section_dict)
        logger.info(f"Created {new_section}")

    SectionControlPanel(
        video=video.serialize(),
        jellyfin_status={"status": "offline"},
        event_create_section=create_section,
        event_delete_all_sections=delete_all_sections,
    )
