import dataclasses
from pathlib import Path
from typing import Optional, cast

import solara
import solara.lab
from loguru import logger
from hmtc.assets.colors import Colors
from hmtc.config import init_config
from hmtc.db import (
    create_tables,
    download_channel_videos,
    download_playlist_videos,
    import_playlist_info,
    init_db,
    is_db_empty,
    seed_database,
)
from hmtc.models import db_null
from hmtc.utils.general import check_folder_exist_and_writable
from hmtc.utils.my_logging import setup_logging

config = init_config()
env = config["general"]["environment"]



match env:
    case "development":
        color = Colors.DARK
    case "staging":
        color = Colors.LIGHT
    case "testing":
        color = Colors.ERROR
    case "production":
        color = Colors.DARK
    case _:
        color = Colors.ERROR
title = f"{config["app"]["name"]} - {env}"


@logger.catch
def setup_to_fail():
    logger.error("This is a test error message")
    1 / 0


def setup_folders():
    working_folder = Path(config["paths"]["working"])
    storage_folder = Path(config["paths"]["storage"])
    wfs = ["uploads", "downloads", "temp"]
    sfs = ["channels", "playlists", "series", "videos"]
    for folder in wfs:
        path = Path(working_folder) / folder
        path.mkdir(exist_ok=True)
        check_folder_exist_and_writable(path)
    for folder in sfs:
        path = Path(storage_folder) / folder
        path.mkdir(exist_ok=True)
        check_folder_exist_and_writable(path)


def setup():
    setup_folders()
    setup_logging(config)

    db_instance = init_db(db_null, config)

    create_tables(db_instance)

    download = config["running"]["download_on_init"]

    if download and is_db_empty():
        logger.error("Database is empty, initializing tables")
        seed_database()
        download_channel_videos()
        download_playlist_videos()

    logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
    logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")

    return db_instance


@solara.component
def Layout(children=[]):

    solara.Style(Path("../assets/style.css"))
    
    return solara.AppLayout(
        navigation=False,
        title=title,
        color=str(color),
        sidebar_open=False,
        children=children,
    )


db = setup()
