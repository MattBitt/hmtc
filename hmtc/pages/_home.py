import dataclasses
from pathlib import Path
from typing import Callable, Dict, Optional, cast

import solara
import solara.lab
from flask import session
from loguru import logger

from hmtc.assets.icons.icon_repo import Icons
from hmtc.components.function_button.main import FunctionButton
from hmtc.components.shared import MyButton, MyList
from hmtc.components.transitions.swap import SwapTransition
from hmtc.config import init_config
from hmtc.domains.base_domain import BaseDomain
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


def asdf(*item):
    logger.debug(f"Running function {item}")
    return True


@solara.component
def Home():
    UsersHomePage()


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
