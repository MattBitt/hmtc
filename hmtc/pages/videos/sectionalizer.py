import solara
from loguru import logger

from hmtc.components.section.details import SectionPages
from hmtc.components.sectionalizer import Sectionalizer
from hmtc.components.shared import PaginationControls
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


time_cursor = solara.reactive(0)


@solara.component
def Page():
    router = solara.use_router()
    video_id = parse_url_args()
    video = Video(video_id)
    current_page = solara.use_reactive(1)
    per_page = 2
    _sections, num_items, num_pages = video.sections_paginated(
        current_page=current_page, per_page=per_page
    )
    sections = solara.use_reactive([Section(x) for x in _sections])

    # Current video time
    def create_section(section):
        start = section["start"] * 1000
        end = section["end"] * 1000
        _section = Section.create(
            {
                "start": start,
                "end": end,
                "section_type": "instrumental",
                "video_id": video.instance.id,
            }
        )

        sections.set(sections.value + [_section])
        logger.success(f"Created section for {video} from {start} to {end}")

    if refresh.value > 0:
        with solara.Column(classes=["main-container"]):
            Sectionalizer(
                video=video,
                sections=sections,
                create_section=create_section,
                time_cursor=time_cursor,
            )
            
            SectionPages(video=video, sections=sections)
            PaginationControls(
                current_page=current_page, num_pages=num_pages, num_items=num_items
            )
