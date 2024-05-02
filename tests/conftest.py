import pytest
import os

from hmtc.config import init_config
from hmtc.db import init_db, create_tables, drop_tables
from hmtc.utils.my_logging import setup_logging
from hmtc.models import db_null


@pytest.fixture(scope="session", autouse=True)
def db():
    db_instance = init_db(db_null, config)
    create_tables(db_instance)
    yield (db_instance, config)
    drop_tables(db_instance)


os.environ["ENVIROMENT"] = "testing"
config = init_config()
setup_logging(config)
