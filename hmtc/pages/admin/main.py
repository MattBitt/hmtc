import solara


@solara.component
def MainAdmin():
    level = solara.use_route_level()  # returns 2
    route_current, routes_current_level = solara.use_route()
    solara.Markdown(f"Main Admin Component")
    solara.Text(f"{level=}")
    solara.Text(f"{route_current=}")
    solara.Text(f"{routes_current_level=}")
