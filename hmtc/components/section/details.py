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

    if sect.instance.comments is not None:
        c = sect.instance.comments
    else:
        c = ""
    comment = solara.use_reactive(c)

    _section_id = sect.instance.id

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
                disabled=(sect.instance.track.get_or_none() is not None),
            )
            with solara.Column(margin=1):
                InputAndDisplay(
                    comment, "Comments", create=create_comment, remove=remove_comment
                )


@solara.component
def SectionPages(video: Video, sections):
    # used by the sectionalizer page

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
