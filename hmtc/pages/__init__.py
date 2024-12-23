from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import solara
import solara.lab
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
from hmtc.utils.importer.seed_database import seed_database_from_json
from hmtc.utils.my_logging import setup_logging


# sets the color of the app bar based on the current dev enviorment
def get_app_bar_color() -> str:
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


def main(config):
    setup_folders(config)
    setup_logging(config)

    db_instance = init_db(db_null, config)

    if config["general"]["environment"] == "development":
        drop_all_tables(db_instance)
        create_tables(db_instance)
        run_migrations(db_instance)
        seed_database_from_json(db_instance)
    else:
        create_tables(db_instance)
        run_migrations(db_instance)

    logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
    logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")


# this is the base of the app
@solara.component
def Layout(children=[]):

    solara.Style(Path("../../assets/style.css"))
    solara.lab.theme.dark = False
    return solara.AppLayout(
        navigation=False,
        title="Main Title",
        color=get_app_bar_color(),
        sidebar_open=False,
        children=children,
    )


config = init_config()
main(config)
