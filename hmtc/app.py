import time
from pathlib import Path
from typing import Any, Dict

import redis
from celery import Celery

1
import solara
import solara.lab
import solara.server.flask
from flask import Flask, g, make_response, request
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.config import init_config
from hmtc.db import (
    create_tables,
    drop_all_tables,
    init_db,
)
from hmtc.models import db_null
from hmtc.utils.db_migrator import run_migrations
from hmtc.utils.general import check_folder_exist_and_writable
from hmtc.utils.importer.existing_files import import_existing_video_files_to_db
from hmtc.utils.importer.seed_database import seed_database_from_json
from hmtc.utils.my_logging import setup_logging



# sets the color of the app bar based on the current dev enviorment
def get_app_bar_color() -> str:
    config = init_config()
    env = config["general"]["environment"]
    match env:
        case "development":
            color = Colors.ERROR
        case "staging":
            color = Colors.WARNING
        case "production":
            color = Colors.PRIMARY
        case _:
            color = Colors.SUCCESS
    return str(color)


def setup_folders(config):
    WORKING = Path(config["WORKING"])
    STORAGE = Path(config["STORAGE"])

    working_folders = ["downloads"]

    storage_folders = ["videos", "tracks"]

    for folder in working_folders:
        path = WORKING / folder
        path.mkdir(exist_ok=True, parents=True)
        check_folder_exist_and_writable(path)

    for folder in storage_folders:
        path = STORAGE / folder
        path.mkdir(exist_ok=True, parents=True)
        check_folder_exist_and_writable(path)

def make_celery(app):
    celery = Celery(
        app.name,
        backend="redis://localhost:6379/0",
        broker="redis://localhost:6379/0"
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['hmtc.slow_funcs.example'])
    return celery


def main(config):
    setup_folders(config)
    setup_logging(config)

    db_instance = init_db(db_null, config)

    if config["general"]["environment"] == "development":
        _STORAGE = Path(config["STORAGE"]) / "videos"
        drop_all_tables(db_instance)
        create_tables(db_instance)
        run_migrations(db_instance)
        seed_database_from_json(db_instance)
        import_existing_video_files_to_db(_STORAGE)

    else:
        create_tables(db_instance)
        run_migrations(db_instance)

    logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
    logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")
    app = Flask(__name__)

    app.register_blueprint(solara.server.flask.blueprint, url_prefix="/")

    return app


config = init_config()
app = main(config)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"
celery = make_celery(app)



@app.route("/hello")
def hello_world():
    from hmtc.slow_funcs import count_words_at_url, example
    example.delay(3)
    return f"Hello from Flask"


if __name__ == "__main__":
    app.debug = True  # Enable debug mode for template auto-reload
    app.run()
