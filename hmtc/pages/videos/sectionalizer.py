import solara
from loguru import logger

from hmtc.components.section.selector import Page as SectionSelector
from hmtc.components.sectionalizer import NewTopicVue, Sectionalizer
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
def NewTopic(sections, selected):
    new_item = solara.use_reactive("")
    error = solara.use_reactive("")
    success = solara.use_reactive("")
    if len(sections.value) == 0:
        return solara.Text(f"No Sections found")

    section = sections.value[selected.value]

    def create_topic(topic_input):
        if error.value != "":
            error.set("")
        if success.value != "":
            success.set("")
        logger.debug(f"Creating new topic {topic_input} if possible")
        if len(topic_input) <= 1:
            error.set(f"Value {topic_input} too short.")
        else:
            try:
                _section = Section(section["id"])
                topic = _section.add_topic(topic=topic_input)
                new_item.set("")
                success.set(f"{topic} was created!")
                refresh.set(refresh.value + 1)

            except Exception as e:
                error.set(f"Error {e}")

    def reset(*args):
        new_item.set("")
        error.set("")
        success.set("")

    with solara.Card():
        NewTopicVue(create=create_topic, reset=reset)
    # with solara.Card():
    #     with solara.Columns([6, 6]):
    #         solara.InputText(label="Topic", value=new_item)
    #         with solara.Row():
    #             solara.Button(
    #                 label="Create Topic", on_click=create_topic, classes=["button"]
    #             )
    #             solara.Button(label="Reset Form", on_click=reset, classes=["button"])
    #     if success.value:
    #         solara.Success(f"{success}")
    #     elif error.value:
    #         solara.Error(f"{error}")


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
        logger.debug(f"After Creating section from {start} to {end}")

    with solara.Column(classes=["main-container"]):
        Sectionalizer(video=video, create_section=create_section)
        SectionSelector(video=video, sections=sections, selected=selected)
        if refresh.value > 0:
            NewTopic(sections=sections, selected=selected)
