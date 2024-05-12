from pathlib import Path
import solara
from loguru import logger

from hmtc.config import init_config
from hmtc.db import (
    create_tables,
    init_db,
    is_db_empty,
    download_channel_videos,
    download_playlist_videos,
    import_playlist_info,
)
from hmtc.models import db_null
from hmtc.utils.general import check_folder_exist_and_writable
from hmtc.utils.my_logging import setup_logging

config = init_config()


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
    config = init_config()
    setup_folders()
    setup_logging(config)

    db_instance = init_db(db_null, config)
    if is_db_empty(db_instance):

        logger.error("Database is empty, initializing tables")
        create_tables(db_instance)
        if config["running"]["download_on_init"]:
            download_channel_videos()
            download_playlist_videos()
        logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
        logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")
    return db_instance


db = setup()


@solara.component
def Layout(children=[]):
    logger.debug("Creating App Layout")
    return solara.AppLayout(
        children=children, color="teal", sidebar_open=False, navigation=True
    )
