import solara
from loguru import logger


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")
