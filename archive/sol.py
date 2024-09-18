import solara
import solara.lab

github_url = solara.util.github_url(__file__)


@solara.component
def VideoPage():
    solara.Markdown("Video")


@solara.component
def About():
    solara.Markdown("About")


def sidebar(name="mizzle"):
    with solara.Sidebar():
        with solara.Card("I am in the sidebar"):
            with solara.Column():
                solara.SliderInt(label="Ideal for placing controls")
                solara.Button(
                    label="View source",
                    icon_name="mdi-github-circle",
                    attributes={"href": github_url, "target": "_blank"},
                    text=True,
                    outlined=True,
                )
                # solara.Markdown(f"You are at: {name}")
                # # bunch of buttons which navigate to our dynamic route
                # with solara.Row():
                #     for subpage in subpages:
                #         with solara.Link(subpage):
                #             solara.Button(label=f"Go to: {subpage}")


def main_content():
    with solara.Card("Main content"):
        solara.Markdown("This is the main content")
        solara.Button(
            label="View source",
            icon_name="mdi-github-circle",
            attributes={"href": github_url, "target": "_blank"},
            text=True,
            outlined=True,
        )

    with solara.Card("Use solara.Columns to create relatively sized columns"):
        with solara.Columns([1, 2, 1]):
            solara.Success("I'm in the first column")
            solara.Warning("I'm in the second column, I am twice as wide")
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


routes = [
    solara.Route(path="/", component=VideoPage, label="home"),
    solara.Route(path="about", component=About, label="about"),
]


@solara.component
def Layout(children):
    route, routes = solara.use_route()

    return solara.AppLayout(children=children)
