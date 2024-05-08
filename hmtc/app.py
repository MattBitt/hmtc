from flask import Flask
import solara.server.flask
from redis import Redis
from rq import Queue
from rq.job import Job
from worker import conn
import time
from utils.tasks import long_task2

app = Flask(__name__)
# app.register_blueprint(solara.server.flask.blueprint, url_prefix="/solara/")
redis = Redis(host="127.0.0.1", port=6379)
q = Queue(connection=conn)

url = "asdf"


@app.route("/")
def hello_world():

    return "Hi Earth"


@app.route("/redis")
def redis_counter():
    redis.incr("hits")
    return "This page has been visited {} times.".format(redis.get("hits"))


@app.route("/task")
def task_route():
    job = q.enqueue_call(func=long_task2, args=(18,), result_ttl=5000)
    print(job.get_id())
    return "All done"


@app.route("/task/<job_key>")
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8741)
