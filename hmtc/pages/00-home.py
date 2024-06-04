import solara
import solara.lab
from loguru import logger

from hmtc.config import init_config


updating = solara.reactive(False)
config = init_config()


@solara.component_vue("./button.vue")
def MyButton():
    pass


@solara.component_vue("../components/pages/Landing.vue")
def LandingPage():
    pass


@solara.component_vue("../components/login/LoginComp.vue")
def LoginForm(event_login, event_register, event_forgot_password):
    pass


@solara.component_vue("../components/login/RegisterComp.vue")
def RegisterForm(event_login, event_forgot_password):
    pass


@solara.component_vue("../components/login/ForgotPassword.vue")
def ForgotPassword(event_login, event_register):
    pass


class State:

    @staticmethod
    def login(*args):
        logger.info(f"Login: {args}")

    @staticmethod
    def register(*args):
        logger.info(f"Register: {args}")

    @staticmethod
    def forgot_password(*args):
        logger.info(f"Forgot Password: {args}")


@solara.component
def Sidebar():

    with solara.Sidebar():
        MyButton()
        # with solara.Column(align="start"):
        #     with solara.Link("/"):

        #         solara.Markdown("asdf")
        #     with solara.Link("/"):
        #         solara.Text("Home", classes=["sidebarbutton"])
        #     with solara.Link("/media/videos"):
        #         solara.Text("Videos", classes=["sidebarbutton"])
        #     with solara.Link("/media/playlists"):
        #         solara.Text("Playlists", classes=["sidebarbutton"])
        #     with solara.Link("/media/channels"):
        #         solara.Text("Channels", classes=["sidebarbutton"])
        #     # solara.Link("Videos", to="/media/videos", classes=["sidebarbutton"])
        #     # solara.Link("Playlists", to="/media/playlists", classes=["sidebarbutton"])
        #     with solara.Row(justify="center"):
        #         solara.Button(
        #             icon=True,
        #             icon_name="mdi-video",
        #         )
        #         solara.Button(
        #             icon=True,
        #             icon_name="mdi-playlist-music",
        #         )
        #         solara.Button(icon=True, icon_name="mdi-music-rest-eighth")


@solara.component
def Page():
    Sidebar()
    LandingPage()

    solara.Markdown("Home Page!")

    # LoginForm(
    #     event_login=State.login,
    #     event_register=State.register,
    #     event_forgot_password=State.forgot_password,
    # )
    # RegisterForm(
    #     event_login=State.login,
    #     event_forgot_password=State.forgot_password,
    # )
    # ForgotPassword(
    #     event_login=State.login,
    #     event_register=State.register,
    # )
