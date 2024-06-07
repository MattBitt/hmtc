import solara
from loguru import logger


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
    version = "0.0.3"

    def sidebar_clicked(item):
        # need to add a check to make sure the route is existing
        router.push(item)
        return
        logger.info(f"Sidebar Clicked: {item}")
        if item == "Recent":
            router.push("/recent")
        elif item == "Videos":
            router.push("/videos")
        elif item == "Playlists":
            router.push("/playlists")
        elif item == "Channels":
            router.push("/channels")
        elif item == "Settings":
            router.push("/settings")
        elif item == "About":
            router.push("/about")
        elif item == "Series":
            router.push("/series")

        else:
            logger.error(f"Unknown sidebar item: {item}")

    with solara.Sidebar():
        _Sidebar(
            version=version,
            router=router,
            event_sidebar_clicked=sidebar_clicked,
        )
