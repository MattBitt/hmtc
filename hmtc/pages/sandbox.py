import solara
from loguru import logger
from typing import Callable
from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("../components/section/section_item.vue", vuetify=True)
def SectionItem(
    event_button_click: Callable[[dict], None],
    event_set_start_time: Callable[[str], None],
    event_set_end_time: Callable[[str], None],
    event_set_section_type: Callable[[str], None],
    event_load_next_section: Callable[[dict], None],
    event_load_previous_section: Callable[[dict], None],
    section=dict(id=15, start="00:00:00", end="23:59:59", duration=74685),
    editing=False,
):
    pass


@solara.component_vue("../components/digits/digit_label.vue", vuetify=True)
def DigitLabel(
    label="default label for DigitalLabel",
    timestamp=dict(id=159, timestamp=12),
    event_enable_editing: Callable[[dict], None] = lambda data: logger.error(
        f"Default Function Call= {data}"
    ),
):
    pass


@solara.component_vue("../components/digits/digit_input.vue", vuetify=True)
def DigitInput(
    label="default label for DigitalInput",
    timestamp=dict(id=387, timestamp=1203),
):
    pass


@solara.component_vue("../components/section/section_timeline.vue", vuetify=True)
def SectionLine(
    timestamps=dict(
        whole_start=0,
        whole_end=2447,
        part_start=600,
        part_end=1200,
    )
):
    pass


@solara.component_vue("../components/topic/topics_list.vue", vuetify=True)
def TopicsList(topics=["Topic 1", "Topic 2", "Topic 3"]):
    pass


@solara.component_vue("../components/shared/logo.vue")
def Logo():
    pass


def complicated_function(*args):
    logger.error(f"Running complicated Function with rgs = {args}")
    return args[0]


def set_section_type(*args):
    logger.error(f"Args = {args}")
    return args[0]


def load_next_section(*args):
    logger.debug("Loading Next Section:")
    # next_section(args[0])


def load_previous_section(*args):
    logger.debug("Loading Previous Section:")
    logger.error(f"Args = {args}")
    return args[0]


def func1(*args):
    logger.error(f"Calling Function 1 with args = {args}")
    return None


### need functions below for refactoring 8-27-24


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    editing_start = solara.use_reactive(False)
    editing_end = solara.use_reactive(True)
    new_topic = solara.use_reactive("")
    topics = solara.use_reactive(["football", "cats", "dogs"])
    video = dict(id=17, duration=1080)
    section = dict(id=15, start=182, end=687)
    start = dict(id=15, timestamp=section["start"], hour=1, minute=3, second=5)
    end = dict(id=37, timestamp=section["end"], hour=2, minute=3, second=4)

    def add_topic():
        if new_topic.value:
            topics.value.append(new_topic.value)
            new_topic.value = ""

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Sandbox")

        with solara.Card(
            elevation=10,
            margin="2",
        ):
            with solara.ColumnsResponsive(6, 6):
                with solara.Card():
                    with solara.Row():
                        solara.InputText(label="Topic", value=new_topic)
                        solara.Button(label="Add Topic", on_click=add_topic),
                    TopicsList(topics=topics.value)

                with solara.Card():
                    SectionLine(
                        timestamps=dict(
                            whole_start=0,
                            whole_end=video["duration"],
                            part_start=section["start"],
                            part_end=section["end"],
                        )
                    )

            with solara.ColumnsResponsive(6, 6):

                with solara.Card():
                    with solara.Column():
                        with solara.Row():
                            solara.Button(
                                label="Toggle Edit Mode",
                                on_click=lambda: editing_start.set(
                                    not editing_start.value
                                ),
                            )

                        if editing_start.value:
                            with solara.Row():
                                DigitInput(
                                    label="Start Time",
                                    timestamp=start,
                                )
                        else:
                            with solara.Row():
                                DigitLabel(
                                    label="Start Time",
                                    timestamp=start,
                                )
                with solara.Card():
                    with solara.Column():
                        with solara.Row():
                            solara.Button(
                                label="Toggle Edit Mode",
                                on_click=lambda: editing_end.set(not editing_end.value),
                            )
                        if editing_end.value:

                            with solara.Row():
                                DigitInput(
                                    label="End Time",
                                    timestamp=end,
                                )
                        else:
                            with solara.Row():
                                DigitLabel(
                                    label="End Time",
                                    timestamp=end,
                                    event_enable_editing=lambda data: logger.error(
                                        f"Event Enable Editing Called = {data}"
                                    ),
                                )
