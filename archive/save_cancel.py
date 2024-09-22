import solara
from typing import Callable


@solara.component
def SectionSaveCancel(
    save: Callable = None,
    cancel: Callable = None,
):
    with solara.Row(justify="center"):
        solara.Button(
            label="Save",
            icon_name="mdi-content-save",
            on_click=save,
            classes=["button"],
        )
        solara.Button(
            label="Cancel",
            icon_name="mdi-cancel",
            on_click=cancel,
            classes=["button"],
        )
