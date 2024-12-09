import solara
from loguru import logger


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    if level == 0:
        return
    else:
        return router.parts[2:]
