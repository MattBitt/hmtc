import logging
import os
import random
import time

import psycopg2
import pytest
from psycopg2.sql import SQL

from hmtc.pages import config
from tests import helpers as test_helpers

logging.basicConfig(format="%(message)s")


os.environ["ENVIROMENT"] = "testing"


def get_cursor():
    """
    Gets a psycopg2 cursor for the parent Database
    """
    conn = psycopg2.connect(
        dbname=config.get("DATABASE", "NAME"),
        user=config.get("DATABASE", "USER"),
        password=config.get("DATABASE", "PASSWORD"),
        host=config.get("DATABASE", "HOST"),
        port=config.get("DATABASE", "PORT"),
    )

    conn.set_isolation_level(0)

    return conn.cursor()


def create_database(db_name: str):
    cur = get_cursor()

    cur.execute(SQL(f"create database {db_name};"))
    cur.execute(SQL(f"grant all privileges on database {db_name} to postgres;"))


def drop_database(db_name: str):
    cur = get_cursor()

    cur.execute(SQL(f"drop database {db_name};"))


def create_random_db():
    time_str = "".join(str(time.time()).split("."))
    random.seed()
    pref = random.randint(1111, 9999)

    random_db = "postgres_" + "_".join([time_str, str(pref)])
    create_database(random_db)

    return random_db


@pytest.fixture(scope="session", autouse=True)
def use_random_db(request):
    """
    Forces each parallell worker to generate and use their own random DB.
    This is the key to letting us test in parallell!
    """
    rand_db = create_random_db()
    test_helpers.random_db_name = rand_db
    logging.warning("\n creating db " + str(rand_db) + "\n")

    def after_all_worker_tests():
        logging.warning("\n dropping db " + str(rand_db) + "\n")
        drop_database(rand_db)

    request.addfinalizer(after_all_worker_tests)
