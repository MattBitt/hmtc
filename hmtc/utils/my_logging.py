import logging
import sys
from pathlib import Path

from loguru import logger

log_stderr_format = (
    "<white>{time: HH:mm:ss.SSS} | </white>"
    "<white>{module} | </white>"
    "<lvl>{message: <80}</lvl>"
)

log_tofile_format = (
    "<white>{time: HH:mm:ss.SSS} | </white>"
    "<white>{module} | </white>"
    "<lvl>{message: <80}</lvl>"
)


def setup_logging(config):
    env = config["general"]["environment"]
    log_level = config["running"]["log_level"]
    log_file_path = config["paths"]["logs"]

    logger.remove()  # remove initial loguru logger

    # disable werkzeug (Flask) logs
    log = logging.getLogger("werkzeug")
    log.disabled = True

    logger.add(
        sys.stderr,
        format=log_stderr_format,
        level=log_level,
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    if env != "production":
        logger.add(
            Path(log_file_path) / "hmtc.log",
            format=log_tofile_format,
            level=log_level,
            rotation="10 MB",
            colorize=False,
            backtrace=False,
            diagnose=False,
        )
    logger.debug(f"Log Level is currently {log_level}")
    return logger
