
import redis
from rq import Queue
from hmtc.utils.tasks.slow_funcs import example, count_words_at_url
import time 

r = redis.Redis.from_url("redis://localhost:6379/0")
q = Queue("high", connection=r)
job = q.enqueue(count_words_at_url, "http://nvie.com")
print(job.return_value())
time.sleep(5)
print(job.return_value())