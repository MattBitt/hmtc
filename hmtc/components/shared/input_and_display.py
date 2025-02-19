import solara

from hmtc.components.transitions.swap import SwapTransition


@solara.component
def MyInput(label, value, on_value):
    solara.InputText(label=label, value=value, on_value=on_value)


@solara.component
def MyLabel(item, remove):

    with solara.Row():
        solara.Text(f"{item.value}", classes=["primary--text", "mt-4"])
        solara.Button(
            icon_name="mdi-delete", classes=["button mywarning"], on_click=remove
        )


@solara.component
def InputAndDisplay(item, label, create, remove):
    with SwapTransition(show_first=(item.value == ""), name="fade"):
        MyInput(label=label, value=item, on_value=create)
        MyLabel(item, remove)
