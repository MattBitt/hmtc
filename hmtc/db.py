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
    Channel,
    Section,
    SectionTopic,
    Series,
    Superchat,
    SuperchatSegment,
    Topic,
    Track,
    TrackBeat,
    User,
    Video,
    YoutubeSeries,
    YoutubeSeriesVideo,
    YoutubeSeriesVideo,
    AlbumTrack,
    AlbumVideo,
]


def create_tables(db, tables=[]):
    if not tables:
        tables = TABLES
    db.create_tables(tables)
    # to resolve the circular depedency between Video and YoutubeSeriesVideo
    # may not need...
    # YoutubeSeriesVideo._schema.create_foreign_key(YoutubeSeriesVideo.video)


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
