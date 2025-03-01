import dataclasses
from pathlib import Path
from typing import Dict, Optional, cast

import solara
import solara.lab
from flask import session
from loguru import logger

from hmtc.components.check_and_fix.main import CheckAndFix
from hmtc.config import init_config
from hmtc.domains.user import User
from hmtc.pages.toolbar.toolbar import MainToolbar
from hmtc.pages.users.main import UsersHomePage
from hmtc.routes import admin_routes, api_routes
from hmtc.utils.general import get_app_bar_color

config = init_config()
STORAGE = Path(config["STORAGE"])
WORKING = Path(config["WORKING"])

config = init_config()
env = config["general"]["environment"]


# move this to its own folder in component once its 'finished'
@solara.component
def CheckAndFix():
    solara.Text(f"local and refreshing automagically!")


@solara.component
def Home():
    UsersHomePage()
    CheckAndFix()


@solara.component
def MyLayout(children=[]):
    with solara.AppLayout(
        children=children,
        navigation=False,
        sidebar_open=False,
        color=get_app_bar_color(config["general"]["environment"]),
    ):
        with solara.AppBar():
            MainToolbar()


api_routes = api_routes()
admin_routes = admin_routes()
routes = [
    solara.Route(
        path="/",
        component=Home,
        label="Home",
        layout=MyLayout,
    ),
    api_routes,
    admin_routes,
]
