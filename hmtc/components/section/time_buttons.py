import solara
from typing import Callable


@solara.component
def SectionTimeButtons(
    small_forward: Callable = None,
    small_backward: Callable = None,
    large_forward: Callable = None,
    large_backward: Callable = None,
    tiny_forward: Callable = None,
    tiny_backward: Callable = None,
):
    with solara.Row(justify="center"):
        solara.Button(
            label="-5",
            icon_name="mdi-step-backward-2",
            on_click=large_backward,
            classes=["button"],
        )
        solara.Button(
            label="-1",
            icon_name="mdi-step-backward",
            on_click=small_backward,
            classes=["button"],
        )
        solara.Button(
            label="-.25",
            icon_name="mdi-step-backward",
            on_click=tiny_backward,
            classes=["button"],
        )
        solara.Button(
            label="+.25",
            icon_name="mdi-step-forward",
            on_click=tiny_forward,
            classes=["button"],
        )
        solara.Button(
            label="+1",
            icon_name="mdi-step-forward",
            on_click=small_forward,
            classes=["button"],
        )

        solara.Button(
            label="+5",
            icon_name="mdi-step-forward-2",
            on_click=large_forward,
            classes=["button"],
        )
