import solara


@solara.component
def Page():
    solara.Markdown("Hello, World! on the Dashboards Index Page")
    solara.Markdown(f"one more time")
    solara.Text(f"Can you this???")
