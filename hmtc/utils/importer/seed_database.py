import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.db import create_tables, drop_all_tables, init_db
from hmtc.domains import Album, Series, User, YoutubeSeries
from hmtc.models import Video as VideoModel
from hmtc.models import db_null

config = init_config()

STORAGE = config["STORAGE"]


def rename_vids_for_albums(db_instance):
    vids = VideoModel.select().order_by(VideoModel.upload_date.asc())
    if len(vids) < 4:
        logger.error("Not enough videos")
        return
    for i, vid in enumerate(vids[:5]):
        vid.title = f"Omegle Bars {i}"
        vid.unique_content = True
        vid.save()
    for i, vid in enumerate(vids[5:8:]):
        vid.title = f"Guerrilla Bars {i}"
        vid.unique_content = True
        vid.save()
    for vid in vids[8:]:
        vid.unique_content = True
        vid.save()


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
