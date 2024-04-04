import solara
from hmtc.components.app_bar import AppBar

clicks = solara.reactive(0)


@solara.component
def Page():
    AppBar()
    with solara.Column():
        color = "green"
        if clicks.value >= 5:
            color = "red"

        def increment():
            clicks.value += 1
            print("clicks", clicks)  # noqa

        solara.Button(label=f"Clicked: {clicks}", on_click=increment, color=color)
