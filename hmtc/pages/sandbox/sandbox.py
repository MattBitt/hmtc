import solara
from loguru import logger

from hmtc.components.shared.ok_cancel import OkCancel
from hmtc.components.shared.sidebar import MySidebar


@solara.component
def Page():
    router = solara.use_router()
    logger.error(f"router: {router.parts}")
    MySidebar(router)

    def func1(*args):
        logger.debug("OK from the main page!!!!")

    def func2(*args):
        logger.debug("CANCEL from the main page!!!!")

    with solara.Column(classes=["main-container"]):
        OkCancel(message="Are you sure?", func_ok=func1, func_cancel=func2)
