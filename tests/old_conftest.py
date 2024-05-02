import pytest
import os
from peewee import PostgresqlDatabase
from hmtc.config import init_config
from functools import wraps
from playhouse.sqlite_ext import JSONField
from playhouse.test_utils import test_database


def connect_to_db(config):
    db_name = config.get("DATABASE", "NAME")
    user = config.get("DATABASE", "USER")
    password = config.get("DATABASE", "PASSWORD")
    host = config.get("DATABASE", "HOST")
    port = config.get("DATABASE", "PORT")
    return PostgresqlDatabase(
        db_name, user=user, password=password, host=host, port=port
    )


os.environ["ENVIROMENT"] = "testing"

config = init_config()
db = connect_to_db(config)
db.connect()


@pytest.fixture
def x():
    return 15


@pytest.fixture
def y():
    return 18


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = PostgresqlDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator
