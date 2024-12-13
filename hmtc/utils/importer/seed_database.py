import json
import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.db import create_tables, drop_all_tables, init_db
from hmtc.domains.album import Album
from hmtc.domains.artist import Artist
from hmtc.domains.beat import Beat
from hmtc.domains.channel import Channel
from hmtc.domains.disc import Disc
from hmtc.domains.section import Section
from hmtc.domains.series import Series
from hmtc.domains.superchat import Superchat
from hmtc.domains.superchat_segment import SuperchatSegment
from hmtc.domains.topic import Topic
from hmtc.domains.track import Track
from hmtc.domains.user import User
from hmtc.domains.video import Video
from hmtc.domains.youtube_series import YoutubeSeries
from hmtc.models import db_null

config = init_config()


def seed_database_from_json(db_instance):
    logger.debug("Checking if database is empty")
    num_channels = Channel.count()
    if num_channels > 2:
        logger.debug("Database is not empty, skipping seeding")
        return

    logger.debug("Seeding database from seed_data.json")
    with open("hmtc/utils/importer/seed_data.json", "r") as f:
        data = json.load(f)
    for channel in data["Channel"]:
        Channel.create(channel)
    for series in data["Series"]:
        Series.create(series)

    for album in data["Album"]:
        Album.create(album)

    for yt_series in data["YoutubeSeries"]:
        YoutubeSeries.create(yt_series)

    for artist in data["Artist"]:
        Artist.create(artist)
    for beat in data["Beat"]:
        Beat.create(beat)

    for disc in data["Disc"]:
        Disc.create(disc)

    for video in data["Video"]:
        Video.create(video)

    # reversed so the 'next' section is created before the 'previous' section
    for section in reversed(data["Section"]):
        Section.create(section)

    for track in data["Track"]:
        Track.create(track)

    for superchat in data["Superchat"]:
        Superchat.create(superchat)
    for superchat_segment in reversed(data["SuperchatSegment"]):
        SuperchatSegment.create(superchat_segment)

    for topic in data["Topic"]:
        Topic.create(topic)

    for user in data["User"]:
        User.create(user)

    logger.success("Database seeded from seed_data.json")


def recreate_database(_db):
    logger.debug("Recreating database")
    drop_all_tables(_db)
    create_tables(_db)
    seed_database_from_json(_db)
    logger.success("Database recreated")


if __name__ == "__main__":
    recreate_database()
