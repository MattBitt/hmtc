import logging
import sys


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


# settings.py (or settings obj)
# LOG_LEVEL = "DEBUG"  # (or 10 if `logging.DEBUG`)
# custom handlers removed, we catch logs via loguru
UVICORN_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "loggers": {
        "uvicorn": {"level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO", "propagate": False},
    },
}


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(config):
    config["general"]["environment"]
    log_level = config["running"]["log_level"]

    # 🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣
    # This seems to work (10-2-24), but the logs are FULL of other information.
    # I need to figure out how to filter out the logs that I don't want.
    # keeping for now
    # logging.root.handlers = [InterceptHandler()]
    # logging.root.setLevel(log_level)

    # # remove every other logger's handlers
    # # and propagate to root logger
    # # noinspection PyUnresolvedReferences
    # for name in logging.root.manager.loggerDict.keys():
    #     logging.getLogger(name).handlers = []
    #     logging.getLogger(name).propagate = True

    # # configure loguru
    # logger.configure(handlers=[{"sink": sys.stdout, "serialize": False}])
    # 🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣🟣

    logger.remove()  # remove initial loguru logger

    # # disable werkzeug (Flask) logs
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

    logger.debug(f"Log Level is currently {log_level}")
    return logger


if __name__ == "__main__":
    config = dict(
        general=dict(environment="dev"),
        running=dict(log_level="DEBUG"),
    )
    setup_logging(config)
