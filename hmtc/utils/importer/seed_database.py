import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.db import create_tables, drop_all_tables, init_db
from hmtc.domains import Album, Series, User, YoutubeSeries
from hmtc.models import db_null

config = init_config()

STORAGE = config["STORAGE"]


def seed_database_from_json(db_instance):
    logger.debug("Seeding database from seed_data.json")
    with open("hmtc/utils/importer/seed_data.json", "r") as f:
        data = json.load(f)

    for series in data["Series"]:
        Series.create(series)

    for album in data["Album"]:
        Album.create(album)

    for yt_series in data["YoutubeSeries"]:
        series = Series.get_by(title=yt_series["series"]["title"])
        yt_series["series_id"] = series.instance.id
        YoutubeSeries.create(yt_series)

    for user in data["User"]:
        User.create(user)

    # for artist in data["Artist"]:
    #     Artist.create(artist)

    logger.success("Database seeded from seed_data.json")


def recreate_database(_db=None):
    if _db is None:
        _db = init_db(db_null, config)

    logger.debug("Recreating database")
    drop_all_tables(_db)
    create_tables(_db)
    seed_database_from_json(_db)
    logger.success("Database recreated")


if __name__ == "__main__":
    recreate_database()
