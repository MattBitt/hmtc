import os
import shutil
from pathlib import Path

import solara
from loguru import logger


from hmtc.config import init_config
from hmtc.db import create_tables, init_db, is_db_empty
from hmtc.models import db_null

# from hmtc.utils.general import check_folder_exist_and_writable
from hmtc.utils.my_logging import setup_logging

config = init_config()


def setup_folders():
    working_folder = Path(config["paths"]["working"])
    storage_folder = Path(config["paths"]["storage"])

    # check_folder_exist_and_writable(working_folder)
    # check_folder_exist_and_writable(storage_folder)


def setup():
    config = init_config()
    setup_folders()
    setup_logging(config)
    db_instance = init_db(db_null, config)
    if is_db_empty(db_instance):
        # not an error, just emphasizing that the database is empty
        logger.error("Database is empty, initializing tables")
        create_tables(db_instance)

        logger.error(f"Current ENVIRONMENT = {config['general']['environment']}")
        logger.error(f"Current LOG_LEVEL = {config['running']['log_level']}")
    return db_instance


db = setup()
