import dataclasses
from pathlib import Path
from typing import Dict, Optional, cast

import solara
import solara.lab
from flask import session
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.config import init_config
from hmtc.domains.channel import Channel
from hmtc.domains.series import Series
from hmtc.domains.user import User
from hmtc.pages.admin.main import MainAdmin
from hmtc.pages.home.main import HomePage
from hmtc.pages.toolbar import MainToolbar
from hmtc.pages.users.main import UsersHomePage
from hmtc.utils.importer.existing_files import (
    create_video_from_folder,
)
from hmtc.utils.importer.seed_database import recreate_database
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.youtube_functions import fetch_ids_from, get_video_info

config = init_config()
STORAGE = Path(config["STORAGE"])
WORKING = Path(config["WORKING"])


# sets the color of the app bar based on the current dev enviorment
def get_app_bar_color() -> str:
    config = init_config()
    env = config["general"]["environment"]
    match env:
        case "development":
            color = Colors.ERROR
        case "staging":
            color = Colors.WARNING
        case "production":
            color = Colors.PRIMARY
        case _:
            color = Colors.SUCCESS
    return str(color)


def check_auth(route, children):
    public_paths = ["/", "signup", "login"]
    admin_paths = ["admin", "auth"]

    if route.path in public_paths:
        children_auth = children
    elif "api" not in route.path:
        logger.error(f"'API' doesn't appear in this {route=}")
        children_auth = []
    else:
        if user.value is None:
            children_auth = [LoginForm()]
        else:
            if route.path in admin_paths and not user.value.admin:
                children_auth = [solara.Error("You are not an admin")]
            else:
                children_auth = children + [UsersHomePage()]
    return children_auth


@dataclasses.dataclass
class UserDC:
    username: str
    admin: bool = False


user = solara.reactive(cast(Optional[UserDC], None))
login_failed = solara.reactive(False)


def login(username: str, password: str):
    # this function can be replace by a custom username/password check
    existing = User.get_by(username=username)
    if existing is None:
        logger.error("User not found.")
        login_failed.value = True
        return None
    hashed = User.hash_password(password)
    if existing.instance.hashed_password == hashed:
        user.value = UserDC(existing.instance.username, existing.instance.is_admin)
        login_failed.value = False
    else:
        login_failed.value = True


@solara.component_vue("./auth/Login.vue")
def _LoginPage(event_login):
    pass


@solara.component_vue("./auth/SignUp.vue")
def _SignUpPage(event_signup=None):
    pass


@solara.component
def SignUpPage():
    def signup(user):
        logger.error(f"About to create a new user: {user=}")

        new_user = User.create(user)
        if new_user is None:
            login_failed.set(True)
        else:
            logger.debug(f"User {new_user} created.")

    _SignUpPage(event_signup=signup)


@solara.component
def LoginForm():
    username = solara.use_reactive("")
    password = solara.use_reactive("")

    def actually_login(item):
        logger.debug(f"Logging {item} into DB")
        login(item["username"], item["password"])

    with solara.Card("Login"):
        _LoginPage(event_login=actually_login)
        if login_failed.value:
            solara.Error("Wrong username or password")


@solara.component
def MyLayout(children=[]):
    route, routes = solara.use_route(peek=True)

    if route is None:
        return solara.Error("Route not found")

    children = check_auth(route, children)

    if user.value and user.value.admin:
        show_nav = True
    else:
        show_nav = False

    with solara.AppLayout(
        children=children,
        navigation=show_nav,
        sidebar_open=False,
        color=get_app_bar_color(),
    ):
        with solara.AppBar():
            if user.value is not None:
                MainToolbar(user)
            else:
                with solara.Link(f"/api/users/"):
                    solara.Button("Login", classes=["button"])


routes = [
    # route level == 0
    solara.Route(path="/", component=SignUpPage, label="Sign Up", layout=MyLayout),
    solara.Route(
        path="api",
        children=[
            solara.Route(
                path="login",
                component=LoginForm,
                label="Login",
                layout=MyLayout,
            ),
            solara.Route(
                path="signup",
                component=SignUpPage,
                label="Create a New Account",
                layout=MyLayout,
            ),
            solara.Route(
                path="users",
                component=UsersHomePage,
                label="User's Home",
                children=[],
            ),
            solara.Route(
                path="admin",
                component=MainAdmin,
                label="Admin",
            ),
        ],
    ),
]
