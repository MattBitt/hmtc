from typing import Callable

import solara
from loguru import logger

from hmtc.domains.section import Section
from hmtc.domains.video import Video


@solara.component_vue("./SectionSelector.vue", vuetify=True)
def SectionSelectorVue(
    sections,
    selected,
    video_duration,
    event_remove_section,
    event_create_topic,
    event_update_selected,
    event_remove_topic,
):
    pass


@solara.component
def SectionSelector(video: Video, sections):
    new_topic = solara.use_reactive("")

    def create_topic(args):
        section_id = args["section_id"]
        topic_string = args["topic_string"]
        if topic_string == "":
            logger.error(f"Input too short for a new topic.")
            return
        ss = Section(section_id)
        section_topic = ss.add_topic(topic_string)
        new_section = [ss.serialize()]
        _sections = [
            x for x in sections.value if x["id"] != ss.instance.id
        ] + new_section
        sorted_sections = sorted(_sections, key=lambda d: d["start"])
        sections.set(sorted_sections)

        logger.debug(f"Created topic {section_topic.topic.text}")

    def remove_topic(args):
        section_id = args["section_id"]
        topic_id = args["topic_id"]
        Section(section_id).remove_topic(topic_id)
        new_section = [Section(section_id).serialize()]
        _sections = [x for x in sections.value if x["id"] != section_id] + new_section
        sorted_sections = sorted(_sections, key=lambda d: d["start"])
        sections.set(sorted_sections)
        logger.success(f"Topic ID {topic_id} removed from Section {section_id}")

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

    def remove_section(section):
        _sect = Section.get_by(id=section["id"])
        logger.debug(f"Remove section {_sect}")
        _sect.delete()
        a = []
        a[:] = [d for d in sections.value if d.get("id") != section["id"]]
        sections.set(a)

    SectionSelectorVue(
        sections=sections.value,
        video_duration=video.instance.duration * 1000,
        event_create_section=create_section,
        event_create_topic=create_topic,
        event_remove_section=remove_section,
        event_remove_topic=remove_topic,
    )

    if new_topic.value != "":
        logger.debug(f"New topic updated {new_topic.value}")
