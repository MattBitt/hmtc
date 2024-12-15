from peewee_migrate import Router
from peewee import PostgresqlDatabase
from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.models import db_null


def run_migrations(db):
    router = Router(db)
    # Create migration
    # router.create("my_first_migration")

    # Run migration/migrations
    router.run("my_first_migration")

    # Run all unapplied migrations
    router.run()


if __name__ == "__main__":
    config = init_config()
    config["database"]["name"] = "HMTCdevelopment"
    config["database"]["user"] = "postgres"
    config["database"]["password"] = "postgres"
    config["database"]["host"] = "localhost"
    config["database"]["port"] = 5432

    db = init_db(db_null, config)

    if db is None:
        raise Exception("Database is None")

    # if len(db.get_tables()) == 0:
    #     create_tables(db)
    #     seed_database()

    run_migrations(db)
    print("Migrations complete")
