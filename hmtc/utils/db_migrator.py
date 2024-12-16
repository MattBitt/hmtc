from loguru import logger
from peewee import PostgresqlDatabase
from peewee_migrate import Router

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.models import db_null


def run_migrations(db):
    router = Router(db)
    router.run()


if __name__ == "__main__":
    config = init_config()
    db = init_db(db_null, config)

    if db is None:
        raise Exception("Database is None")

    router = Router(db)
    # Create migration
    router.create("db_migration")
    logger.success(
        "New Migrations completed. Update the migration file with the necessary changes."
    )
