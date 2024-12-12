from loguru import logger

from hmtc.config import init_config
from hmtc.models import *

config = init_config()


TABLES = [
    Album,
    AlbumDiscVideo,
    Artist,
    Beat,
    BeatArtist,
    Channel,
    Disc,
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
