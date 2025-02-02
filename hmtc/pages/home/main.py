from pathlib import Path

import solara
import solara.lab

from hmtc.assets.colors import Colors
from hmtc.utils.opencv.image_manager import ImageManager


@solara.component
def HomePage():
    level = solara.use_route_level()  # returns 0
    route_current, routes_current_level = solara.use_route()

    with solara.Column(classes=["main-container"]):

        with solara.Column(align="center", style={"background-color": Colors.SURFACE}):
            logo_image = ImageManager(Path("hmtc/assets/images/harry-mack-logo.png"))
            solara.Image(image=logo_image.image)
            with solara.Row():
                with solara.Link(f"/login"):
                    solara.Button("Login", classes=["button"])
                with solara.Link(f"/api/users/signup"):
                    solara.Button("Create Account", classes=["button"])
