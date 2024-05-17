from pathlib import Path
import dataclasses
from typing import Callable

import reacton.ipyvuetify as v

import solara
from solara.lab.toestand import Ref
import peewee
from peewee import JOIN
import solara
import solara.lab
from loguru import logger
from solara.lab import task

from hmtc.components.file_drop_card import FileDropCard, FileInfo
from hmtc.config import init_config
from hmtc.models import Video, Section
from hmtc.utils.general import time_since_update
from hmtc.utils.section_manager import SectionManager


time_cursor_slider = solara.reactive(0)
title = solara.reactive("")
youtube_id = solara.reactive(False)

updated = solara.reactive(False)


config = init_config()

UPLOAD_PATH = Path(config["paths"]["working"]) / "uploads"


# our model for a todo item, immutable/frozen avoids common bugs
@dataclasses.dataclass(frozen=True)
class SectionItem:
    id: int
    start: int
    end: int
    section_type: str
    is_first: bool
    is_last: bool
    ordinal: int
    previous_section: Section
    next_section: Section

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            start=model.start,
            end=model.end,
            section_type=model.section_type,
            is_first=model.is_first,
            is_last=model.is_last,
            ordinal=model.ordinal,
            previous_section=model.previous_section,
            next_section=model.next_section,
        )


@solara.component
def SectionEdit(
    section_item: solara.Reactive[SectionItem],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    """Takes a reactive section item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(section_item.value)

    def save():
        section_item.value = copy.value
        on_close()

    with solara.Card("Edit", margin=0):
        solara.InputText(label="Ordinal", value=Ref(copy.fields.ordinal))
        solara.InputText(label="Start", value=Ref(copy.fields.start))
        solara.InputText(label="End", value=Ref(copy.fields.end))
        with solara.CardActions():
            v.Spacer()
            solara.Button(
                "Save",
                icon_name="mdi-content-save",
                on_click=save,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Close",
                icon_name="mdi-window-close",
                on_click=on_close,
                outlined=True,
                text=True,
            )
            solara.Button(
                "Delete",
                icon_name="mdi-delete",
                on_click=on_delete,
                outlined=True,
                text=True,
            )


@solara.component
def SectionListItem(section_item, on_delete):
    """Displays a single section item, modifications are done 'in place'.

    For demonstration purposes, we allow editing the item in a dialog as well.
    This will not modify the original item until 'save' is clicked.
    """
    edit, set_edit = solara.use_state(False)
    with solara.Card():
        with solara.Row():
            solara.Button(
                icon_name="mdi-delete",
                icon=True,
                on_click=lambda: on_delete(section_item.value),
            )
            solara.Checkbox(
                value=Ref(section_item.fields.is_first)
            )  # , color="success")
            solara.Checkbox(
                value=Ref(section_item.fields.is_last)
            )  # , color="success")
            solara.InputText(label="Ordinal", value=Ref(section_item.fields.ordinal))
            solara.InputText(label="Start Time", value=Ref(section_item.fields.start))
            solara.InputText(label="End Time", value=Ref(section_item.fields.end))
            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )
        with v.Dialog(
            v_model=edit, persistent=True, max_width="500px", on_v_model=set_edit
        ):
            if edit:  # 'reset' the component state on open/close

                def on_delete_in_edit():
                    on_delete(section_item.value)
                    set_edit(False)

                SectionEdit(
                    section_item,
                    on_delete=on_delete_in_edit,
                    on_close=lambda: set_edit(False),
                )


@solara.component
def SectionNew(video, on_new):
    """Component that managed entering new section items"""

    def add_initial_section():
        logger.debug(f"Adding initial section to video {video.title}")
        Section.create(
            video=video,
            start=0,
            end=video.duration,
            section_type="INITIAL",
            is_first=True,
            is_last=True,
            ordinal=1,
        )
        logger.debug(f"Updating: {video.title}")
        logger.debug(f"Finished adding section")
        on_new()

    solara.Button("Create a New section", on_click=add_initial_section)


@solara.component
def VideoHeader(video):
    with solara.Card(title=video.title):
        solara.Markdown(f"ID: {video.id}")
        solara.Markdown(f"Youtube ID: {video.youtube_id}")
        solara.Markdown(f"Duration: {video.duration}")


@solara.component
def VideoSections(video, sm, on_new, on_delete):

    def add_section():
        sm.split_section_at(time_cursor_slider.value)
        on_new()

    def on_delete_local(section_id):
        sect = Section.get_or_none(Section.id == section_id)
        if sect is not None:
            on_delete(sect)
        on_new()

    title.set(video.title)
    sm = SectionManager(video)
    with solara.ColumnsResponsive(12):
        with solara.Column():
            if video.poster is not None:
                solara.Image(video.poster, width="300px")
            solara.InputText(label="Name", value=title, continuous_update=False)

            if video.sections.count() > 0:
                solara.Markdown(f"Sections: {video.sections.count()}")
                solara.Markdown(f"Duration: {video.duration}")
                solara.Markdown(f"Current Timestamp: {time_cursor_slider.value}")
                solara.SliderInt(
                    label="Timestamp",
                    value=time_cursor_slider,
                    max=video.duration,
                )
                solara.Button(
                    "Add section at timestamp",
                    on_click=add_section,
                )

                with solara.ColumnsResponsive(6, large=4):
                    for sect in sm.section_list:
                        with solara.Card(f"Order: {sect.ordinal}"):
                            solara.Markdown(f"Start:{sect.start} End:{sect.end}")
                            solara.Markdown(f"Type: {sect.section_type}")
                            solara.Markdown(f"First: {sect.is_first}")
                            solara.Markdown(f"Last: {sect.is_last}")
                            if sect.previous_section is not None:
                                if sect.previous_section.get_or_none() is not None:
                                    solara.Markdown(
                                        f"Previous: {sect.previous_section.get().ordinal}"
                                    )
                            if sect.next_section is not None:
                                if sect.next_section.get_or_none() is not None:
                                    solara.Markdown(
                                        f"Next: {sect.next_section.get().ordinal}"
                                    )

                            solara.Button(
                                f"Merge with Next Section",
                                on_click=lambda: sm.merge_sections(
                                    sect, sect.next_section
                                ),
                                disabled=sect.is_last,
                            )
                            solara.Button(
                                f"Delete Section",
                                on_click=lambda: on_delete_local(sect.id),
                            )


class State:

    def __init__(self, video_id):
        self.video_id = video_id
        self.section_query = Section.select().join(Video).where(Video.id == video_id)
        self.sections = solara.reactive(self.section_query)

    def on_new(self):
        self.sections.value = (
            Section.select().join(Video).where(Video.id == self.video_id)
        )

    def on_delete(self, item):

        sect = Section.get_or_none(Section.id == item.id)
        if sect is not None:
            sect.my_delete_instance()
            logger.success(f"Deleted section {item.id}")
        else:
            logger.error(f"Could not delete section {item.id}")
        self.sections.value = (
            Section.select().join(Video).where(Video.id == self.video_id)
        )


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        return

    video_id = router.parts[level:][0]

    if video_id.isdigit():
        state = State(video_id)

        video = (
            Video.select()
            .join(Section, join_type=JOIN.LEFT_OUTER)
            .where(Video.id == video_id)
            .get_or_none()
        )
        if video is None:
            return solara.Markdown("No Video Found")

        VideoHeader(video)

        # VideoSections(video, on_new=state.on_new, on_delete=state.on_delete)

        SectionNew(video, on_new=state.on_new)
        if state.sections.value:
            for item in state.sections.value:
                SectionListItem(
                    solara.Reactive(SectionItem.from_model(item)),
                    on_delete=state.on_delete,
                )
