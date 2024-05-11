import sys
from pathlib import Path

from loguru import logger


def setup_logging(config):
    env = config["general"]["environment"]
    log_level = config["running"]["log_level"]
    log_file_path = config["paths"]["logs"]

    logger.remove()
    log_format = (
        "<white>{time: HH:mm:ss.SSS} | </white>"
        "<white>{module} | </white>"
        "<lvl>{message: <80}</lvl>"
    )
    # logger.configure(extra={"classname": "None"})
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    if env != "production":
        logger.add(
            Path(log_file_path) / "hmtc.log",
            format=log_format,
            level=log_level,
            colorize=False,
            backtrace=True,
            diagnose=True,
        )
    logger.debug(f"Log Level is currently {log_level}")
    return logger
