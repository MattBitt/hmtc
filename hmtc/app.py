import time
from pathlib import Path
from typing import Any, Dict

import redis
import solara
import solara.lab
import solara.server.flask
from flask import Flask, g, make_response, render_template, request, session
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
from hmtc.utils.importer.seed_database import (
    rename_vids_for_albums,
    seed_database_from_json,
)
from hmtc.utils.my_logging import setup_logging


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
        # rename_vids_for_albums(db_instance)

    else:
        create_tables(db_instance)
        run_migrations(db_instance)

    logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
    logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")
    app = Flask(__name__)

    app.register_blueprint(solara.server.flask.blueprint, url_prefix="/")
    app.secret_key = "ETw3$d%+[^j%Q6y^sbMI4n**QSl6SA"
    return app


config = init_config()
app = main(config)


@app.route("/flask")
def index():
    if "visits" in session:
        session["visits"] = session.get("visits") + 1
    else:
        session["visits"] = 1
    return f"You have visited this page {session['visits']} times"


@app.route("/logout")
def logout():
    if "current_user" in session:
        session.pop("current_user")
        # logger.debug(f"Clearing current user {session['current_user']}")


@app.before_request
def before_request_func():
    bad_paths = ["/_solara", "/static", "/jupyter"]
    for path in bad_paths:
        if request.path.startswith(path):
            return None

    # logger.debug(f"Before request {request.path=} of a regular path object")


if __name__ == "__main__":
    app.debug = True  # Enable debug mode for template auto-reload
    app.run()
