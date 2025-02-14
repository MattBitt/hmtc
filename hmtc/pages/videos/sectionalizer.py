import solara
from loguru import logger

from hmtc.components.section.selector import Page as SectionSelector
from hmtc.components.sectionalizer import Sectionalizer
from hmtc.domains.section import Section
from hmtc.domains.topic import Topic
from hmtc.domains.video import Video

refresh = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


@solara.component
def Page():

    video_id = parse_url_args()
    video = Video(video_id)
    current_page = solara.use_reactive(1)
    per_page = 6
    _sections, num_items, num_pages = video.sections_paginated(
        current_page=current_page, per_page=per_page
    )
    sections = solara.use_reactive([Section(x).serialize() for x in _sections])
    selected = solara.use_reactive(0)

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
        selected.set(len(sections.value))
        logger.debug(f"After Creating section from {start} to {end}")

    with solara.Column(classes=["main-container"]):
        Sectionalizer(video=video, create_section=create_section)
        SectionSelector(video=video, sections=sections)

