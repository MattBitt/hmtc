import solara
from loguru import logger


@solara.component_vue("OkCancel.vue", vuetify=True)
def _OkCancel(dialog, message, event_pyok, event_pycancel):
    pass


dialog = solara.reactive(False)


def event_ok(func, *args, **kwargs):
    func()
    dialog.set(False)


def event_cancel(func, *args, **kwargs):
    func()
    dialog.set(False)


@solara.component
def OkCancel(message, func_ok, func_cancel):

    solara.Button("Toggle Dialog", on_click=lambda: dialog.set(not dialog.value))
    solara.Text(f"Current Dialog Value: {dialog.value}")
    _OkCancel(
        dialog=dialog.value,
        message=message,
        event_pyok=lambda x: event_ok(func_ok),
        event_pycancel=lambda x: event_cancel(func_cancel),
    )
