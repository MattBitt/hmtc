from typing import Callable
from loguru import logger
import numpy as np
import solara

seed = solara.reactive(42)


@solara.component_vue("mycard2.vue")
def MyCard2(
    event_button_click: Callable[[dict], None],
    event_set_start_time: Callable[[str], None],
    event_set_end_time: Callable[[str], None],
    event_set_section_type: Callable[[str], None],
    section=dict(id=15, start="00:00:00", end="23:59:59"),
):
    pass


@solara.component
def Page():
    start_time = solara.use_reactive("00:00:00")
    end_time = solara.use_reactive("23:59:59")
    section_type = solara.use_reactive("UNKNOWN")

    def complicated_function(*args):
        logger.error(f"Args = {args}")
        return args[0]

    def set_section_type(*args):
        logger.error(f"Args = {args}")
        return args[0]

    with solara.Column(style={"min-width": "600px"}):

        MyCard2(
            section=dict(
                id=147,
                start=start_time.value,
                end=end_time.value,
                is_first=True,
                is_last=True,
                section_type=section_type.value,
            ),
            event_set_start_time=lambda data: start_time.set(
                complicated_function(data)
            ),
            event_set_end_time=lambda data: end_time.set(complicated_function(data)),
            event_set_section_type=lambda data: section_type.set(
                set_section_type(data)
            ),
        )
