import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from hmtc.config import init_config
from hmtc.models import *
from hmtc.utils.general import get_youtube_id

config = init_config()
WORKING = Path(config["paths"]["working"])
STORAGE = Path(config["paths"]["storage"])

MEDIA_INFO = Path(os.environ.get("HMTC_CONFIG_PATH")) / "media_info"

TABLES = [
    Album,
    Artist,
    Beat,
    BeatArtist,
    Bird,
    BirdFile,
    Channel,
    File,
    FileType,
    Section,
    SectionTopics,
    Series,
    Superchat,
    SuperchatFile,
    SuperchatSegment,
    Topic,
    Track,
    TrackBeat,
    User,
    Video,
    YoutubeSeries,
]


def create_tables(db, tables=[]):
    if not tables:
        tables = TABLES
    db.create_tables(tables)


def drop_all_tables(db):
    db.drop_tables(TABLES)


def init_db(db, config):
    db.init(
        database=config["database"]["name"],
        user=config["database"]["user"],
        password=config["database"]["password"],
        host=config["database"]["host"],
        port=config["database"]["port"],
    )
    return db


def is_db_empty():
    vids = Video.select(Video.id).count()
    logger.debug(f"DB currently has: {vids} Videos")
    return vids < 10


def import_existing_video_files_to_db(path):
    # havent tested in a million years, but might be a good starting point
    # for the file import
    found = 0
    unfound = 0
    f = Path(path)
    for file in f.glob("**/*.*"):
        if file.is_file():
            youtube_id = get_youtube_id(file.stem)
            if youtube_id:
                vid = Video.get_or_none(Video.youtube_id == youtube_id)
                if not vid:
                    unfound = unfound + 1
                    continue
                else:
                    logger.debug(
                        f"Successfully found video{vid.youtube_id}. Adding file"
                    )
            else:
                logger.debug(f"Could not find youtube_id in {file}")

    logger.success("Finished importing files to the database.")
    logger.debug(f"Found {found} new files.")
    logger.debug(f"There were {unfound} files found with no associated video")

    if not f.exists():
        logger.error("Path not found")
        return None
    return f.glob("**/*")
