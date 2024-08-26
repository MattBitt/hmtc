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
    section=dict(id=15, start="00:00:00", end="23:59:59", duration=74685),
    event_enable_editing: Callable[[dict], None] = lambda data: logger.error(
        f"Default Function Call= {data}"
    ),
):
    pass


@solara.component_vue("../components/digits/digit_input.vue", vuetify=True)
def DigitInput(
    label="default label for DigitalInput",
    section=dict(id=15, start="00:00:00", end="23:59:59", duration=74685),
):
    pass


@solara.component_vue("./sandbox.vue")
def Sandbox(playbackTime=0):
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


@solara.component
def Page():
    MySidebar(router=solara.use_router())

    editing_start = solara.use_reactive(False)
    editing_end = solara.use_reactive(True)

    with solara.Column(classes=["main-container"]):
        solara.Markdown("## Sandbox")

        # use this to test out new vue components
        # just change the contents of the vue file and refresh the page
        with solara.Card(
            elevation=10,
            margin="2",
        ):
            Sandbox(event_trigger=lambda data: logger.error("asdf"))
            with solara.Card():
                solara.Markdown("## Placeholder for Words")

            with solara.ColumnsResponsive(6, 6):
                with solara.Column():
                    with solara.Row():
                        solara.Button(
                            label="Enable",
                            on_click=lambda: editing_start.set(True),
                        )
                        solara.Button(
                            label="Disable",
                            on_click=lambda: editing_start.set(False),
                        )
                    if editing_start.value:
                        with solara.Row():
                            DigitInput(label="Start Time")
                    else:
                        with solara.Row():
                            DigitLabel(label="Start Time")
                with solara.Column():
                    with solara.Row():
                        solara.Button(
                            label="Enable",
                            on_click=lambda: editing_end.set(True),
                        )
                        solara.Button(
                            label="Disable",
                            on_click=lambda: editing_end.set(False),
                        )
                    if editing_end.value:

                        with solara.Row():
                            DigitInput(label="End Time")
                    else:
                        with solara.Row():
                            DigitLabel(
                                label="End Time",
                                event_enable_editing=lambda data: logger.error(
                                    f"Event Enable Editing Called = {data}"
                                ),
                            )

                #     SectionItem(
                #         section=dict(
                #             id=15,
                #             start="00:01:02",
                #             end="01:02:03",
                #             is_first=False,
                #             is_last=False,
                #             section_type="Instrumental",
                #             start_string="04:07:16",
                #             end_string="12:13:19",
                #         ),
                #         event_set_start_time=lambda data: logger.debug(
                #             f"Start Time = {data}"
                #         ),
                #         event_set_end_time=lambda data: logger.debug(
                #             f"End Time = {data}"
                #         ),
                #         event_set_section_type=lambda data: logger.debug(
                #             f"Section Type  = {data}"
                #         ),
                #         event_load_next_section=lambda data: logger.debug(
                #             f"Loading Next Section {data}"
                #         ),
                #         event_load_previous_section=lambda data: logger.debug(
                #             f"Loading Previous Section {data}"
                #         ),
                #         editing=editing_start.value,
                #     )
                # with solara.Column():
                #     with solara.Row():
                #         solara.Button(
                #             label="Enable", on_click=lambda: editing_end.set(True)
                #         )
                #         solara.Button(
                #             label="Disable", on_click=lambda: editing_end.set(False)
                #         )
                #     SectionItem(
                #         section=dict(
                #             id=15,
                #             start="00:01:02",
                #             end="01:02:03",
                #             is_first=False,
                #             is_last=False,
                #             section_type="Instrumental",
                #             start_string="04:07:16",
                #             end_string="12:13:19",
                #         ),
                #         event_set_start_time=lambda data: func1(data),
                #         event_set_end_time=lambda data: logger.debug(
                #             f"End Time = {data}"
                #         ),
                #         event_set_section_type=lambda data: logger.debug(
                #             f"Section Type  = {data}"
                #         ),
                #         event_load_next_section=lambda data: logger.debug(
                #             f"Loading Next Section {data}"
                #         ),
                #         event_load_previous_section=lambda data: logger.debug(
                #             f"Loading Previous Section {data}"
                #         ),
                #         editing=editing_end.value,
                #     )
