import sys

from loguru import logger


def setup_logging(config):
    log_level = config["running"]["log_level"]
    logger.remove()
    log_format = (
        "<white>{time: HH:mm:ss.SSS} | </white>"
        "<white>{module} | </white>"
        "<lvl>{message: <80}</lvl>"
    )
    # logger.configure(extra={"classname": "None"})
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)
    logger.debug(f"Log Level is currently {log_level}")
    return logger
