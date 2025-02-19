from typing import Callable

import solara
from loguru import logger

from hmtc.domains.section import Section
from hmtc.domains.video import Video


@solara.component_vue("./SectionSelector.vue", vuetify=True)
def SectionSelectorVue(
    sections,
    video_duration,
    event_remove_section,
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

    def create_title(args):
        logger.debug(f"creating title args = {args}")
        section_id = args["section_id"]
        title_string = args["title_string"]
        sect = Section.get_by(id=section_id)
        sect.instance.title = title_string
        sect.instance.save()

    def remove_title(args):
        logger.debug(f"removing title args = {args}")

    def create_comment(args):
        logger.debug(f"creating comment args = {args}")
        section_id = args["section_id"]
        comment_string = args["comment_string"]
        sect = Section.get_by(id=section_id)
        sect.instance.comment = comment_string
        sect.instance.save()

    def remove_comments(args):
        logger.debug(f"removing comment args = {args}")

    SectionSelectorVue(
        sections=sections.value,
        video_duration=video.instance.duration * 1000,
        event_remove_section=remove_section,

    )
