import solara
import solara.lab
from hmtc.components.my_app_bar import MyAppBar
from hmtc.pages import app_state

from typing import Callable

import numpy as np


seed = solara.reactive(42)


@solara.component_vue("mycard2.vue")
def MyCardasdf(
    event_goto_report: Callable[[dict], None],
    value=[1, 10, 30, 20, 3],
    caption="My Card",
    color="red",
    dialog=True,
):
    pass


def main_content():
    with solara.Card("Main content"):
        solara.Markdown("This is the main content")
        solara.Button(
            label="View source",
            icon_name="mdi-github-circle",
            attributes={"href": "www.google.com", "target": "_blank"},
            text=True,
            outlined=True,
        )

    with solara.Card("Use solara.Columns to create relatively sized columns"):
        with solara.ColumnsResponsive(6, large=4):
            solara.Success("I'm in the first column")
            solara.Warning("I'm in the second column, I am twice as wide")
            solara.Warning("I'm in the third column, I should match the first")
            solara.Warning("I'm in the third column, I should match the first")

        with solara.Card("Use solara.Column to create a full width column"):
            with solara.Column():
                solara.Success("I'm first in this full with column")
                solara.Warning("I'm second in this full with column")
                solara.Error("I'm third in this full with column")

        with solara.Card("Use solara.ColumnsResponsive to response to screen size"):
            with solara.ColumnsResponsive(6, large=4):
                for i in range(6):
                    solara.Info(
                        "two per column on small screens, three per column on large screens"
                    )


@solara.component
def Page():
    gen = np.random.RandomState(seed=seed.value)
    sales_data = np.floor(np.cumsum(gen.random(7) - 0.5) * 100 + 100)
    show_report = solara.use_reactive(False)
    MyAppBar()
    solara.InputText("Name", value="Some random value", classes=["input1"])
    with solara.Column(style={"min-width": "600px"}):
        if show_report.value:
            with solara.Card("Report"):
                solara.Markdown("Lorum ipsum dolor sit amet")
                solara.Button("Go back", on_click=lambda: show_report.set(False))
        else:

            def new_seed():
                seed.value = np.random.randint(0, 100)

            solara.Button("Generate new data", on_click=new_seed)

            MyCardasdf(
                value=sales_data.tolist(),
                color="red",
                caption="Sales Last 7 Days",
                event_goto_report=lambda data: show_report.set(True),
            )

    # with solara.Column():
    #     main_content()
