from loguru import logger
import solara
from typing import Callable, cast
import ipyvue


def use_event(el: solara.Element, callback: Callable):
    def add_event_handler():
        def on_enter(widget, event, data):
            callback(widget.v_model)

        widget = cast(ipyvue.VueWidget, solara.get_widget(el))
        widget.on_event("keyup.enter", on_enter)

        def cleanup():
            logger.debug("in cleanup")
            widget.on_event("keyup.enter", on_enter, remove=True)

        return cleanup

    solara.use_effect(add_event_handler, dependencies=[])


@solara.component
def Page():
    def function():
        logger.debug("in function")
        return 1 + 1

    input = solara.InputText(label="first")
    use_event(input, function)
