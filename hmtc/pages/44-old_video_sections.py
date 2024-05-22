import dataclasses
from pathlib import Path
from typing import Callable

import reacton.ipyvuetify as v
import solara
import solara.lab
from loguru import logger
from peewee import JOIN
from solara.lab.toestand import Ref

from hmtc.config import init_config
from hmtc.models import Breakpoint, Video

time_cursor_slider = solara.reactive(0)
title = solara.reactive("")
youtube_id = solara.reactive(False)

updated = solara.reactive(False)


config = init_config()

UPLOAD_PATH = Path(config["paths"]["working"]) / "uploads"


@dataclasses.dataclass(frozen=True)
class BreakpointItem:
    id: int
    timestamp: int
    video: Video

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id, timestamp=model.timestamp, video=model.video)

    def save_to_db(self):
        breakpoint = Breakpoint.get_or_none(Breakpoint.id == self.id)
        breakpoint.timestamp = self.timestamp
        breakpoint.save()


@solara.component
def BreakpointEdit(
    breakpoint_item: solara.Reactive[BreakpointItem],
    on_delete: Callable[[], None],
    on_close: Callable[[], None],
):
    """Takes a reactive breakpoint item and allows editing it. Will not modify the original item until 'save' is clicked."""
    copy = solara.use_reactive(breakpoint_item.value)

    def save():
        breakpoint_item.value = copy.value
        on_close()

    with solara.Card("Edit", margin=0):
        solara.InputText(label="Timestamp", value=Ref(copy.fields.timestamp))

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
def BreakpointListItem(breakpoint_item, on_delete):
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
                on_click=lambda: on_delete(breakpoint_item.value),
            )
            solara.InputText(
                label="Timestamp", value=Ref(breakpoint_item.fields.timestamp)
            )
            solara.Markdown(f"Section: {breakpoint_item.fields.section}")
            solara.Button(
                icon_name="mdi-pencil", icon=True, on_click=lambda: set_edit(True)
            )
        with v.Dialog(
            v_model=edit, persistent=True, max_width="500px", on_v_model=set_edit
        ):
            if edit:

                def on_delete_in_edit():
                    on_delete(breakpoint_item.value)
                    set_edit(False)

                BreakpointEdit(
                    breakpoint_item,
                    on_delete=on_delete_in_edit,
                    on_close=lambda: set_edit(False),
                )


@solara.component
def VideoHeader(video):
    with solara.Card(title=video.title):
        solara.Markdown(f"ID: {video.id}")
        solara.Markdown(f"Youtube ID: {video.youtube_id}")
        solara.Markdown(f"Duration: {video.duration}")

        if video.poster:
            solara.Image(video.poster, width="300px")


class State:
    breakpoints = solara.reactive([])

    def __init__(self, video_id):
        self.video = self.load_video(video_id)
        if self.video is None:
            logger.error("No video selected")
            raise ValueError("No video selected")
        State.breakpoints.value = self.video.breakpoints

    def load_video(self, video_id):
        return (
            Video.select()
            .join(Breakpoint, join_type=JOIN.LEFT_OUTER)
            .where(Video.id == video_id)
            .get_or_none()
        )

    @staticmethod
    def reset_breakpoints():
        for bp in State.breakpoints.value:
            bp.my_delete_instance()
        State.breakpoints.value = []
        State.create_initial_breakpoints()

    def create_initial_breakpoints(self):
        Breakpoint.create(video=self.video, timestamp=0)
        Breakpoint.create(video=self.video, timestamp=self.video.duration)

        self.breakpoints.value = Breakpoint.select().where(
            Breakpoint.video_id == self.video.id
        )

    def on_add_breakpoint(self, timestamp):

        Breakpoint.create(video=self.video, timestamp=timestamp)

        self.breakpoints.value = Breakpoint.select().where(
            Breakpoint.video_id == self.video.id
        )

    def on_delete_breakpoint(self, item):
        bp = Breakpoint.get_or_none(Breakpoint.id == item.id)
        if bp is not None:
            bp.my_delete_instance()
            logger.success(f"Deleted breakpoint {item.id}")
        else:
            logger.error(f"Could not delete breakpoint {item.id}")
        self.breakpoints.value = Breakpoint.select().where(
            Breakpoint.video_id == self.video.id
        )


def get_id_from_url():
    router = solara.use_router()
    level = solara.use_route_level()

    if len(router.parts) == 1:
        solara.Markdown("No Video Selected")
        return

    id = router.parts[level:][0]
    if id.isdigit():
        return int(id)


@solara.component
def Page():

    video_id = get_id_from_url()
    try:
        state = State(video_id)
    except ValueError:
        solara.Markdown("No Video Selected")

    with solara.Card(state.video.title):
        VideoHeader(state.video)

        if state.breakpoints.value:
            with solara.Row():
                solara.Button(label="New Breakpoint", on_click=state.on_add_breakpoint)
                solara.Button(
                    label="Reset Breakpoints",
                    on_click=state.reset_breakpoints,
                )
            for item in state.breakpoints.value:
                bp = BreakpointItem.from_model(item)

                BreakpointListItem(
                    solara.Reactive(bp),
                    on_delete=state.on_delete_breakpoint,
                )
        else:
            solara.Markdown("No Breakpoints")
            solara.Button(
                "Create Default Breakpoints",
                on_click=state.create_initial_breakpoints,
            )
