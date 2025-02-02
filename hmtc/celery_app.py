import time

import requests
from celery import Celery
from loguru import logger


def make_celery():
    celery = Celery(
        "worker", backend="redis://redis:6379/0", broker="redis://redis:6379/0"
    )

    return celery


# app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
# app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"
_celery = make_celery()


@_celery.task()
def example(seconds):
    logger.error("Starting task")
    for i in range(seconds):
        logger.debug(i)
        time.sleep(1)
    return "Done"


def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())
