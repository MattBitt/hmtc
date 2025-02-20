from typing import Callable

import solara
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.shared import InputAndDisplay
from hmtc.domains.section import Section
from hmtc.domains.video import Video


@solara.component_vue("./SectionSelector.vue", vuetify=True)
def SectionDetailsVue(
    section,
    video_duration,
    event_remove_section,
):
    pass


@solara.component
def SectionDetails(sect, video, sections, remove_section):

    new_topic = solara.use_reactive("")
    if sect.instance.comments is not None:
        c = sect.instance.comments
    else:
        c = ""
    comment = solara.use_reactive(c)
    new_title = solara.use_reactive("")
    _section_id = sect.instance.id
    _video_id = video.instance.id

    def create_topic(topic_string):
        if topic_string == "":
            logger.error(f"Input too short for a new topic.")
            return
        ss = Section(sect["id"])
        section_topic = ss.add_topic(topic_string)
        new_section = [ss.serialize()]
        _sections = [
            x for x in sections.value if x["id"] != ss.instance.id
        ] + new_section
        sorted_sections = sorted(_sections, key=lambda d: d["start"])
        sections.set(sorted_sections)

        logger.debug(f"Created topic {section_topic.topic.text} for sec")

    def remove_topic(args):
        section_id = args["section_id"]
        topic_id = args["topic_id"]
        Section(section_id).remove_topic(topic_id)
        new_section = [Section(section_id).serialize()]
        _sections = [x for x in sections.value if x["id"] != section_id] + new_section
        sorted_sections = sorted(_sections, key=lambda d: d["start"])
        sections.set(sorted_sections)
        logger.success(f"Topic ID {topic_id} removed from Section {section_id}")

    def create_title(args):
        logger.debug(f"creating title args = {args}")
        section_id = args["section_id"]
        title_string = args["title_string"]
        sect = Section.get_by(id=section_id)
        sect.instance.title = title_string
        sect.instance.save()

    def remove_title(args):
        logger.debug(f"removing title args = {args}")

    def create_comment(comment_string):
        sect = Section.get_by(id=_section_id)
        sect.instance.comments = comment_string
        sect.instance.save()

    def remove_comment():
        sect = Section.get_by(id=_section_id)
        sect.instance.comments = ""
        sect.instance.save()
        comment.set("")

    with solara.Card():
        SectionDetailsVue(
            section=sect.serialize(),
            video_duration=video.instance.duration * 1000,
            event_remove_section=remove_section,
        )

        with solara.Row(justify="space-around"):
            solara.Button(
                label="Delete",
                icon_name=Icons.DELETE.value,
                classes=["button mywarning"],
                on_click=remove_section,
            )
            with solara.Column(margin=1):
                InputAndDisplay(
                    comment, "Comments", create=create_comment, remove=remove_comment
                )


@solara.component
def SectionPages(video: Video, sections):

    def remove_section(section):
        _id = section.instance.id
        section.delete()
        a = []
        a[:] = [d for d in sections.value if d.instance.id != _id]
        sections.set(a)

    for sect in sections.value:
        SectionDetails(
            sect=sect,
            video=video,
            sections=sections,
            remove_section=lambda: remove_section(sect),
        )
