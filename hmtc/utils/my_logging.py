from loguru import logger
import sys


def setup_logging(config):
    log_level = config.get("GENERAL", "LOG_LEVEL")
    logger.remove()
    log_format = (
        "<white>{time: HH:mm:ss.SSS} | </white>"
        "<white>{module} | </white>"
        "<lvl>{message: <80}</lvl>"
        # "<lvl>[{level: <8}] "
        # "</lvl><yellow>{name}  {function}:{line}</yellow>"
    )
    # logger.configure(extra={"classname": "None"})
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)
    logger.debug("Log Level is currently {}".format(config.get("GENERAL", "LOG_LEVEL")))
    return logger
