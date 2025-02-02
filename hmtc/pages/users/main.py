from pathlib import Path

import solara
import solara.lab

from hmtc.assets.colors import Colors
from hmtc.utils.opencv.image_manager import ImageManager


@solara.component
def UsersHomePage():
    level = solara.use_route_level()  # returns 0
    route_current, routes_current_level = solara.use_route()

    with solara.Column(classes=["main-container"]):
        with solara.Row(justify="center", style={"background-color": Colors.SURFACE}):
            with solara.Link("/tables/videos/unique"):
                solara.Button("Videos", classes=["button"])
            with solara.Link("/tables/tracks/"):
                solara.Button("Tracks", classes=["button"])
            with solara.Link("/dashboards/domains/"):
                solara.Button("Domains", classes=["button"], href="/dashboards/domains")
            with solara.Link("/dashboards/files/"):
                solara.Button("Files", classes=["button"], href="/dashboards/domains")

        with solara.Column(align="center", style={"background-color": Colors.SURFACE}):
            logo_image = ImageManager(Path("hmtc/assets/images/harry-mack-logo.png"))
            solara.Image(image=logo_image.image)
