from functools import wraps

from peewee import PostgresqlDatabase

random_db_name = ""  # "global" variable set by conftest.py


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            db_name = random_db_name or "hmtc_testing"

            # why isnt this using the config?

            test_db = PostgresqlDatabase(
                db_name,
                user="postgres",
                password="postgres",
                host="192.168.0.202",
            )
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator
