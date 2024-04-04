import solara
import solara.lab
from hmtc.components.app_bar import AppBar
from hmtc.pages import app_state


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

    AppBar()
    with solara.Column():
        main_content()
