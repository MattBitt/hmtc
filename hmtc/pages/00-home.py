import solara
import solara.lab
from loguru import logger

from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config

updating = solara.reactive(False)
config = init_config()


@solara.component_vue("../components/pages/Landing.vue")
def LandingPage(current_phase, event_login_clicked, event_register_clicked):
    pass


@solara.component_vue("../components/pages/SignIn.vue")
def LoginForm(
    event_login_clicked, event_register_clicked, event_forgot_password_clicked
):
    pass


@solara.component_vue("../components/pages/SignUp.vue")
def RegisterForm(event_login_clicked, event_forgot_password_clicked):
    pass


@solara.component_vue("../components/pages/Home.vue")
def ForgotPassword(event_login_clicked, event_register_clicked):
    pass


class State:
    router = None

    @staticmethod
    def login(*args):
        logger.info("Login clicked")
        State.router.push("/videos")

    @staticmethod
    def register(*args):
        logger.info("Register Clicked")

    @staticmethod
    def forgot_password(*args):
        logger.info("Forgot Password clicked")


@solara.component
def Page():

    State.router = solara.use_router()
    MySidebar(
        router=State.router,
    )
    current_phase = solara.use_reactive("landing")

    def set_phase_to_login(*ignore_args):
        current_phase.set("login")

    def set_phase_to_landing(*ignore_args):
        current_phase.set("landing")

    def set_phase_to_register(*ignore_args):
        current_phase.set("register")

    def set_phase_to_forgot_password(*ignore_args):
        current_phase.set("forgot_password")

    if current_phase.value == "landing":
        LandingPage(
            current_phase=current_phase.value,
            event_login_clicked=set_phase_to_login,
            event_register_clicked=set_phase_to_register,
        )
    elif current_phase.value == "login":
        LoginForm(
            event_login_clicked=State.login,
            event_register_clicked=set_phase_to_register,
            event_forgot_password_clicked=set_phase_to_forgot_password,
        )
    elif current_phase.value == "register":
        RegisterForm(
            event_login_clicked=set_phase_to_login,
            event_forgot_password_clicked=set_phase_to_forgot_password,
        )
    elif current_phase.value == "forgot_password":
        ForgotPassword(
            event_login=set_phase_to_login, event_register_clicked=set_phase_to_register
        )

    else:
        solara.Markdown(f"Home Page! {current_phase.value}")

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
