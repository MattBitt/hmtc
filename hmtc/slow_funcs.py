import time

import requests
from loguru import logger
from hmtc.app import _celery

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
