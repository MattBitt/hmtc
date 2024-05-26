import dataclasses
from typing import Callable
from loguru import logger
import reacton.ipyvuetify as v
from hmtc.models import Video
import solara
from solara.lab.toestand import Ref

from hmtc.mods.section import SectionManager, Section


@solara.component
def SectionEdit(
    section_item: solara.Reactive[Section],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    """Takes a reactive section item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(section_item.value)

    def save():
        section_item.value = copy.value
        on_close()

    with solara.Card("Edit", margin=0):
        solara.InputText(label="ID", value=Ref(copy.fields.id), disabled=True)
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
def SectionListItem(
    section_item: solara.Reactive[Section],
    video,
    on_delete: Callable[[Section], None],
):
    edit, set_edit = solara.use_state(False)

    width = (section_item.value.end - section_item.value.start) / video.duration * 100
    with solara.Card(style=f"width: {width}%", margin=0):
        solara.InputInt(label="ID", value=section_item.value.id)
        solara.Markdown(
            f"Duration: {(section_item.value.end - section_item.value.start)}"
        )
        solara.Markdown(f"Width: {width}%")

        solara.InputInt(label="Start", value=section_item.value.start)
        solara.InputInt(label="End", value=section_item.value.end)
        solara.InputText(
            label="Section Type", value=Ref(section_item.fields.section_type)
        )
        with solara.CardActions():
            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )
            solara.Button(
                icon_name="mdi-delete",
                icon=True,
                on_click=lambda: on_delete(section_item.value),
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
def SectionNew(
    video,
    on_new: Callable[[Section], None],
    on_delete: Callable[[Section], None],
):
    start = solara.reactive(0)
    end = solara.reactive(video.duration)
    section_type = solara.reactive("intro")

    def add_section():

        on_new(
            video=video,
            start=start.value,
            end=end.value,
            section_type=section_type.value,
        )

    def clear_sections():
        sections = Video.get_by_id(video.id).sections
        for section in sections:
            SectionManager.delete_from_db(section)
            on_delete(section)

    with solara.Card("New Section"):
        solara.InputInt(label="Start", value=start)
        solara.InputInt(label="End", value=end)
        solara.InputText(label="Section Type", value=section_type)

        solara.Button("Create", on_click=add_section)
        solara.Button("Clear", on_click=clear_sections)


# We store out reactive state, and our logic in a class for organization
# purposes, but this is not required.
# Note that all the above components do not refer to this class, but only
# to do the Section items.
# This means all above components are reusable, and can be used in other
# places, while the components below use 'application'/'global' state.
# They are not suited for reuse.


class State:

    # sm = SectionManager.from_video(vid)
    # sect = sm.create_section(start=0, end=30, section_type="intro")
    # sect2 = sm.create_section(start=30, end=210, section_type="instrumental")
    # sect3 = sm.create_section(start=210, end=230, section_type="acapella")
    # sect4 = sm.create_section(start=230, end=300, section_type="outro")
    # sections = solara.reactive([])

    @staticmethod
    def load_sections(video_id: int):
        logger.warning(f"Loading sections (from page 31) for video: {video_id}")
        video = Video.get_by_id(video_id)
        sm = SectionManager.from_video(video)
        State.sections = solara.use_reactive(sm.sections)

    @staticmethod
    def on_new(video, start: int, end: int, section_type: str):

        logger.debug(f"Adding new item: {start}, {end}, {section_type}")
        # logger.error(f"Before adding: ({len(State.sm.sections)}) {State.sm.sections}")
        sm = SectionManager.from_video(video)
        sm.create_section(start=start, end=end, section_type=section_type)
        State.sections.value = sm.sections

        logger.error(
            f"after adding: ({len(State.sections.value)}){State.sections.value}"
        )

    @staticmethod
    def on_delete(item: Section):
        logger.debug(f"Deleting item: {item}")
        new_items = list(State.sections.value)
        new_items.remove(item)
        SectionManager.delete_from_db(item)
        State.sections.value = new_items


@solara.component
def SectionStatus():
    """Status of our section list"""
    items = State.sections.value

    count = len(items)
    solara.Info(f"{count} item{'s' if count != 1 else ''} total")
    solara.Error(f"Sections: {[x.id for x in items]}")


@solara.component
def VideoInfo(video):

    solara.Markdown(f"Video: {video.title}")
    solara.Markdown(f"Duration: {video.duration}")


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        raise ValueError("No video selected")

    return router.parts[level:][0]


@solara.component
def Page():
    video_id = parse_url_args()
    State.load_sections(video_id)
    video = Video.get_by_id(video_id)
    with solara.ColumnsResponsive(12, large=4):
        with solara.Card("Video Info"):
            VideoInfo(video)
        SectionNew(video=video, on_new=State.on_new, on_delete=State.on_delete)

    if State.sections.value:
        SectionStatus()
        with solara.Row():
            for index, item in enumerate(State.sections.value):

                section_item = Ref(State.sections.fields[index])
                SectionListItem(section_item, video=video, on_delete=State.on_delete)

    else:
        solara.Info("No section items, enter some text above, and hit enter")
