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
from hmtc.domains.video import Video
from hmtc.pages.admin.main import MainAdmin
from hmtc.pages.auth.login import LoginPage
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
class User:
    username: str
    admin: bool = False


user = solara.reactive(cast(Optional[User], None))
login_failed = solara.reactive(False)


def login(username: str, password: str):
    # this function can be replace by a custom username/password check
    if username == "test" and password == "test":
        user.value = User(username, admin=False)
        login_failed.value = False
    elif username == "admin" and password == "admin":
        user.value = User(username, admin=True)
        login_failed.value = False
    else:
        login_failed.value = True


@solara.component_vue("./auth/Login.vue")
def _LoginPage(event_login_user):
    pass


@solara.component_vue("./auth/SignUp.vue")
def _SignUpPage(event_signup=None):
    pass


@solara.component
def SignUpPage():
    def signup(user):
        logger.error(f"About to create a new user: {user=}")

    _SignUpPage(event_signup=signup)


@solara.component
def _CreateUser(event_create_user=None):
    solara.Markdown(f"Create user Form")


@solara.component
def LoginForm():
    username = solara.use_reactive("")
    password = solara.use_reactive("")

    def actually_login(item):
        logger.debug(f"Logging {item} into DB")
        login(item["username", item["password"]])

    _LoginPage(event_login_user=actually_login)
    with solara.Card("Login"):
        solara.Markdown(
            """
        This is an example login form.

          * use admin/admin to login as admin.
          * use test/test to login as a normal user.
        """
        )
        solara.InputText(label="Username", value=username)
        solara.InputText(label="Password", password=True, value=password)
        solara.Button(
            label="Login", on_click=lambda: login(username.value, password.value)
        )
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
                    component=LoginPage,
                    label="Login",
                    layout=MyLayout,
                ),
                solara.Route(
                    path="signup",
                    component=_CreateUser,
                    label="Create a New Account",
                    layout=MyLayout,
                ),
                solara.Route(
                    path="users",
                    component=UsersHomePage,
                    label="User's Home",
                    layout=MyLayout,
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
