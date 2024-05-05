import os

os.environ["HMTC_ENV"] = "testing"
os.environ["HMTC_CONFIG_PATH"] = "hmtc/config/"
from pathlib import Path

import pytest
from loguru import logger


from hmtc.config import init_config
from hmtc.db import create_tables, drop_tables, init_db
from hmtc.models import db_null
from hmtc.utils.general import my_copy_file
from hmtc.utils.my_logging import setup_logging


config = init_config()

setup_logging(config)

WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

SOURCE_PATH = WORKING / "test_file_input"

# need actual files to test with so folder has to be there
assert SOURCE_PATH.exists()

TARGET_PATH = WORKING / "test_file_output"
TARGET_PATH.mkdir(exist_ok=True)


@pytest.fixture(scope="function", autouse=True)
def db():
    db_instance = init_db(db_null, config)
    create_tables(db_instance)
    yield (db_instance, config)
    drop_tables(db_instance)


@pytest.fixture(scope="function")
def test_files():

    logger.debug(f"source_path: {SOURCE_PATH}")
    assert SOURCE_PATH.exists()
    return [file.name for file in SOURCE_PATH.glob("*")]


@pytest.fixture(scope="function")
def test_image_filename():

    img = [x for x in SOURCE_PATH.glob("*.png")][0]

    if not TARGET_PATH.exists():
        TARGET_PATH.mkdir()

    my_copy_file(img, TARGET_PATH)
    return TARGET_PATH / img.name
