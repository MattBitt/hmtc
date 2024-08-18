from playhouse.migrate import *
from hmtc.db import (
    create_tables,
    download_channel_videos,
    download_playlist_videos,
    import_playlist_info,
    import_youtube_series,
    init_db,
    is_db_empty,
    seed_database,
)
from hmtc.models import db_null, YoutubeSeries
from hmtc.config import init_config


def migration1(db, migrator):
    # This migration adds a new column to the video and series tables to account for
    # 'youtube_series'

    # this is also the first migration. From here out, new dev databases
    # will be created from backups of production (manually)
    # use backup from 8-17-2024

    tables = db.get_tables()
    if "YoutubeSeries" not in tables:
        db.create_tables([YoutubeSeries])

    table_name = "video"
    youtube_series = IntegerField(null=True)

    if table_name not in tables:
        print("Table not found. Migration not possible/required")
        return

    column_name = "youtube_series_id"
    cols = db.get_columns(table_name)
    if column_name in [c.name for c in cols]:
        print(
            f"Column {column_name} already exists. Migration not possible/required. Skipping"
        )

    else:

        migrate(
            migrator.add_column(table_name, column_name, youtube_series),
        )

    table_name2 = "series"
    if table_name2 not in tables:
        print("Table not found. Migration not possible/required")

    cols = db.get_columns(table_name2)
    if column_name in [c.name for c in cols]:
        print(f"Column {column_name} already exists. Migration not possible/required")
    else:

        migrate(
            migrator.add_column(table_name2, column_name, youtube_series),
        )
    ys = YoutubeSeries.select()
    if ys.count() == 0:
        import_youtube_series()


def run_migrations(db):
    migrator = PostgresqlMigrator(db)

    migration1(db, migrator)


if __name__ == "__main__":

    config = init_config()
    config["database"]["name"] = "HMTC"
    config["database"]["user"] = "postgres"
    config["database"]["password"] = "postgres"
    config["database"]["host"] = "192.168.0.202"
    config["database"]["port"] = 5432

    db = init_db(db_null, config)

    if db is None:
        raise Exception("Database is None")

    if config["database"]["name"] == "HMTC":
        print("Database is in production mode. Exiting for now")
        exit(99)

    # if len(db.get_tables()) == 0:
    #     create_tables(db)
    #     seed_database()

    run_migrations(db)
    print("Migrations complete")
