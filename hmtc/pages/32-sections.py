from dataclasses import dataclass, field
from typing import Callable, List

import solara
from loguru import logger
from solara.lab.toestand import Ref


@dataclass
class Section:
    start: int
    end: int
    section_type: str = "unknown"
    video_id: int = field(init=False)
    id: int = field(init=False)

    def __post_init__(self):
        self.video_id = 1  # Hardcoded for now
        self.id = 1  # Hardcoded for now


@dataclass
class SectionManager:
    sections: List[Section] = field(default_factory=list)

    @classmethod
    def find_section_with_breakpoint(cls, time: int):
        logger.debug(f"Finding section with breakpoint at {time}")
        for sect in cls.sections:
            if sect.start <= time <= sect.end:
                return sect

    def add_breakpoint(self, time: int):
        # sect = self.find_section_with_breakpoint(time)
        logger.debug(f"Creating breakpoint at time= {time}")
        logger.debug(f"Current sections (before append): {self.sections}")
        self.sections.append(Section(time, time + 10))
        logger.debug(f"Current sections (after append): {self.sections}")


@dataclass
class MockedVideo:
    id: int
    title: str
    url: str
    duration: int
    sect_man: SectionManager = field(default_factory=SectionManager)


@solara.component
def SectionListItem(
    section: solara.Reactive[Section],
    on_update: Callable[[Section], None],
    on_delete: Callable[[Section], None],
):
    solara.Text(f"Section {section.value.id}: {section.value}")


class State:
    vid = MockedVideo(
        1, "Test Video", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", 300
    )
    time_cursor = solara.reactive(vid.duration // 2)
    sect1 = Section(start=0, end=vid.duration)
    sect2 = Section(start=30, end=60)
    sect3 = Section(start=90, end=120)
    sections = solara.reactive([sect1, sect2, sect3])

    @staticmethod
    def on_new(item):
        logger.debug(f"on_new: {item}, {item.__class__}")
        logger.info(f"Adding new item: {item}")
        # item.save_to_db()
        # State.todos.value = TodoItem.grab_n_from_db(n=10)

    @staticmethod
    def on_delete(item):
        logger.debug(f"on_delete: {item}, {item.__class__}")
        logger.info(f"Deleting item: {item}")
        # db_item = item.grab_id_from_db(id=item.id)
        # db_item.my_delete_instance()
        # State.todos.value = TodoItem.grab_n_from_db(n=10)

    @staticmethod
    def on_update(item):
        logger.debug(f"on_update: {item}, {item.__class__}")
        logger.info(f"Updating existing item: {item}")

    @staticmethod
    def add_section():
        logger.debug("adding section")
        new_section = Section(
            State.time_cursor.value, State.vid.duration, sect_type="new"
        )
        State.sections.value.extend([new_section])


@solara.component
def Page():
    solara.Info("Loaded Successfully!")

    solara.Success(f"Time Cursor: {State.time_cursor.value}")
    solara.SliderInt(
        label="Current Time", value=State.time_cursor, min=0, max=State.vid.duration
    )
    solara.Button("Add Section at cursor", on_click=State.add_section)

    with solara.Card("Section list", style="min-width: 500px"):
        if State.sections.value:
            # TodoStatus()
            with solara.ColumnsResponsive(4):
                for index, item in enumerate(State.sections.value):
                    section_item = Ref(State.sections.fields[index])
                    with solara.Card():
                        SectionListItem(
                            Ref(section_item),
                            on_update=State.on_update,
                            on_delete=State.on_delete,
                        )
        else:
            solara.Info("No todo items, enter some text above, and hit enter")
