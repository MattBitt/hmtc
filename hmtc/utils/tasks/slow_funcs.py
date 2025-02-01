import time
from loguru import logger
import requests

def example(seconds):
    logger.error('Starting task')
    for i in range(seconds):
        logger.debug(i)
        time.sleep(1)
    return "Done"




def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())
