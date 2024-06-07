import solara
from loguru import logger


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


@solara.component_vue("./dropdown.vue")
def _Dropdown(items, caption, event_on_click, color):
    pass


@solara.component
def Dropdown(items, caption, handle_click, color):

    _Dropdown(
        items=items,
        caption=caption,
        event_on_click=handle_click,
        color=color,
    )
