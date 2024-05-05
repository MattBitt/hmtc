import os
from functools import wraps

import pytest
from peewee import PostgresqlDatabase

from hmtc.pages import config


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
