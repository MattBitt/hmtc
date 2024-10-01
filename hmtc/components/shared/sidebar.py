import solara
import solara.lab
from loguru import logger

# program version
VERSION = "0.0.20"


@solara.component_vue("./sidebar.vue")
def _Sidebar(
    version,
    event_sidebar_clicked,
):
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
def MySidebar(
    router,
):
    def sidebar_clicked(item):
        # need to add a check to make sure the route is existing
        router.push(item)
        return

    with solara.AppBar():

        solara.Button(
            icon_name="mdi-home", on_click=lambda: router.push("/"), icon=True
        )
        icon_name = "mdi-logout" if False else "mdi-login"
        solara.Button(
            icon_name=icon_name, on_click=lambda: logger.debug("clicked"), icon=True
        )
        solara.Text(f"{VERSION}", classes=["version-number"])
        # solara.lab.ThemeToggle(enable_auto=False)
        with solara.Sidebar():
            _Sidebar(
                version=VERSION,
                router=router,
                event_sidebar_clicked=sidebar_clicked,
            )
