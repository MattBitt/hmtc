import solara
import solara.lab
from loguru import logger

from hmtc.config import init_config

updating = solara.reactive(False)
config = init_config()


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
def Page():
    LoginForm(
        event_login=State.login,
        event_register=State.register,
        event_forgot_password=State.forgot_password,
    )
    # RegisterForm(
    #     event_login=State.login,
    #     event_forgot_password=State.forgot_password,
    # )
    # ForgotPassword(
    #     event_login=State.login,
    #     event_register=State.register,
    # )
