from pathlib import Path

import solara
from loguru import logger


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
    def delete_all_sections(*args):
        logger.error(f"Deleting all Sections {args}")

    def create_section(*args):
        logger.error(f"Create Section {args}")
        pass

    SectionControlPanel(
        video=VideoItem.serialize(video),
        jellyfin_status={"status": "offline"},
        event_create_section=create_section,
        event_delete_all_sections=delete_all_sections,
    )
